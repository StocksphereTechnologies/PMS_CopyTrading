import React, { useState, useEffect, useRef, useCallback } from "react";
import { Button, Row, Col, Dropdown, Select, Table, Tag, Empty } from "antd";
import { SearchOutlined, DownOutlined, CloseCircleOutlined } from "@ant-design/icons";
import axios from "axios";

const { Option } = Select;

const MarketWatch: React.FC = () => {
    const [open, setOpen] = useState(false);
    const [searchText, setSearchText] = useState("");
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [watchlist, setWatchlist] = useState<any[]>([]);
    const [liveData, setLiveData] = useState<Record<string, any>>({});

    // ══════════════════════════════════════════════════════════
    // LTP Polling: Uses the SAME REST API as search (always works!)
    // No WebSocket complexity, no stale sessions
    // ══════════════════════════════════════════════════════════
    useEffect(() => {
        if (watchlist.length === 0) return;

        const fetchLTP = async () => {
            try {
                const instruments = watchlist.map(item => ({
                    scrip_code: item.scrip_code,
                    exchange: item.exchange,
                    symbol: item.symbol,
                    name: item.name,
                }));

                const response = await axios.post(
                    "http://localhost:8000/api/v1/marketwatch/ltp",
                    { instruments }
                );

                const data = response.data?.data || [];
                setLiveData(prev => {
                    const next = { ...prev };
                    data.forEach((tick: any) => {
                        if (tick.symbol) {
                            next[tick.symbol] = tick;
                        }
                    });
                    return next;
                });
            } catch (err) {
                console.error("LTP fetch error:", err);
            }
        };

        // Fetch immediately on watchlist change
        fetchLTP();

        // Then poll every 3 seconds
        const interval = setInterval(fetchLTP, 3000);
        return () => clearInterval(interval);
    }, [watchlist]);

    // Handle Search with 2+ characters
    const handleSearch = async (val: string) => {
        setSearchText(val);
        if (val.length >= 2) {
            try {
                const response = await axios.get(`http://localhost:8000/api/v1/marketwatch/search`, { 
                    params: { q: val } 
                });
                setSearchResults(response.data.instruments || []);
            } catch (err) {
                console.error("Search error", err);
            }
        } else {
            setSearchResults([]);
        }
    };

    // Add selected symbol to watchlist
    const addToWatchlist = (selected: any) => {
        setWatchlist((prev) => {
            if (prev.find((item) => item.symbol === selected.symbol)) return prev;
            return [...prev, selected];
        });
        setOpen(false);
        setSearchText("");
    };

    // Remove symbol from watchlist
    const removeFromWatchlist = (symbol: string) => {
        setWatchlist(prev => prev.filter(item => item.symbol !== symbol));
        // Also remove from liveData
        setLiveData(prev => {
            const next = { ...prev };
            delete next[symbol];
            return next;
        });
    };

    const columns = [
        { 
            title: "Symbol", 
            key: "symbol", 
            width: '40%',
            render: (record: any) => (
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <b style={{ fontSize: '15px' }}>{record.symbol}</b>
                    <Tag color="geekblue" style={{ marginLeft: 8, fontSize: '10px' }}>{record.exchange}</Tag>
                </div>
            )
        },
        { 
            title: "LTP", 
            key: "ltp", 
            align: 'right' as const,
            render: (record: any) => {
                const tick = liveData[record.symbol];
                // Use live data if available, otherwise use search result price
                const price = (tick?.last_price && tick.last_price > 0) 
                    ? tick.last_price 
                    : (record.last_price || "0.00");
                return <span style={{ fontWeight: 700, fontSize: '15px' }}>₹{price}</span>;
            }
        },
        { 
            title: "Change (%)", 
            key: "change", 
            align: 'right' as const,
            render: (record: any) => {
                const tick = liveData[record.symbol];
                const pct = tick?.change_percent ?? record.change_percent ?? 0;
                const color = pct >= 0 ? "#10b981" : "#ef4444";
                return <span style={{ color, fontWeight: 600 }}>{pct >= 0 ? '+' : ''}{pct}%</span>;
            }
        },
        {
            title: "",
            key: "action",
            align: 'center' as const,
            width: 80,
            render: (record: any) => (
                <Button 
                    type="text" 
                    danger 
                    icon={<CloseCircleOutlined />} 
                    onClick={() => removeFromWatchlist(record.symbol)}
                />
            )
        }
    ];

    const dropdownContent = (
        <div style={{ background: "#fff", padding: "16px", width: 400, boxShadow: "0 10px 25px rgba(0,0,0,0.15)", borderRadius: 12 }}>
            <Select
                showSearch
                autoFocus
                placeholder="Search (e.g. RELIANCE, NIFTY 26400 CE)"
                style={{ width: "100%", marginBottom: 8 }}
                value={searchText || undefined}
                filterOption={false}
                onSearch={handleSearch}
                onSelect={(val) => {
                    const sel = searchResults.find(s => s.symbol === val);
                    if (sel) addToWatchlist(sel);
                }}
                dropdownStyle={{ display: 'none' }}
                open={false}
            />
            
            <div style={{ maxHeight: 300, overflowY: 'auto' }}>
                {searchResults.length > 0 ? (
                    searchResults.map((item) => (
                        <div 
                            key={item.symbol} 
                            onClick={() => addToWatchlist(item)}
                            style={{ 
                                padding: '10px 12px', 
                                cursor: 'pointer', 
                                borderRadius: 6,
                                display: 'flex',
                                justifyContent: 'space-between',
                                borderBottom: '1px solid #f0f0f0'
                            }}
                            className="search-item-hover"
                        >
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <b>{item.symbol}</b>
                                <small style={{ color: '#888' }}>{item.exchange} | {item.name}</small>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontWeight: 600, color: '#14b8a6' }}>₹{item.last_price || '--'}</div>
                                <div style={{ fontSize: '11px', color: (item.change_percent || 0) >= 0 ? 'green' : 'red' }}>
                                    {item.change_percent}%
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    searchText.length >= 2 && <div style={{ padding: 20, textAlign: 'center', color: '#888' }}>No results found</div>
                )}
            </div>
        </div>
    );

    return (
        <div style={{ padding: "24px 40px", maxWidth: 900 }}>
            <Row style={{ marginBottom: 32 }}>
                <Col>
                    <Dropdown 
                        open={open} 
                        onOpenChange={setOpen} 
                        dropdownRender={() => dropdownContent} 
                        trigger={["click"]}
                        placement="bottomLeft"
                    >
                        <Button
                            type="primary"
                            icon={<SearchOutlined />}
                            style={{ 
                                background: "#14b8a6", 
                                borderColor: "#14b8a6", 
                                height: 48, 
                                padding: "0 32px", 
                                borderRadius: 8,
                                fontWeight: 600,
                                fontSize: '15px',
                                boxShadow: '0 4px 14px rgba(20, 184, 166, 0.3)'
                            }}
                        >
                            Search & Add Symbol
                        </Button>
                    </Dropdown>
                </Col>
            </Row>

            <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 4px 20px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
                <Table 
                    dataSource={watchlist} 
                    columns={columns} 
                    rowKey="symbol" 
                    pagination={false} 
                    className="marketwatch-table"
                    locale={{ emptyText: <Empty description="Your watchlist is empty" style={{ padding: 40 }} /> }}
                />
            </div>

            <style>{`
                .search-item-hover:hover {
                    background: #f0fdfa !important;
                }
                .marketwatch-table .ant-table-thead > tr > th {
                    background: #f9fafb;
                    font-weight: 700;
                    color: #4b5563;
                }
            `}</style>
        </div>
    );
};

export default MarketWatch;
// import React, { useState } from "react";
// import { Button, Row, Col, Dropdown, Select } from "antd";
// import { DownOutlined } from "@ant-design/icons";
// import MarketWatchTable from "./MarketWatchTable";

// const { Option } = Select;

// const MarketWatch: React.FC = () => {
//   const [open, setOpen] = useState(false);
//   const [searchText, setSearchText] = useState("");

//   // Dummy symbols (replace later with API)
//   const symbols: string[] = [
//     "NIFTY",
//     "BANKNIFTY",
//     "RELIANCE",
//     "TCS",
//   ];

//   const filteredSymbols =
//     searchText.length >= 2
//       ? symbols.filter((s) =>
//         s.toLowerCase().includes(searchText.toLowerCase())
//       )
//       : [];

//   const dropdownContent = (
//     <div
//       style={{
//         background: "#fff",
//         padding: 10,
//         width: 300,
//         boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
//         borderRadius: 4,
//       }}
//     >
//       <Select
//         showSearch
//         autoFocus
//         placeholder="Search symbol"
//         style={{ width: "100%" }}
//         value={searchText || undefined}
//         filterOption={false}
//         onSearch={(val) => setSearchText(val)}
//         notFoundContent={
//           searchText.length < 2
//             ? "Please enter 2 or more characters"
//             : "No symbol found"
//         }
//       >
//         {filteredSymbols.map((sym) => (
//           <Option key={sym} value={sym}>
//             {sym}
//           </Option>
//         ))}
//       </Select>
//     </div>
//   );

//   return (
//     <div style={{ padding: 16 }}>
//       {/* Search & Add Symbol */}
//       <Row style={{ marginBottom: 12 }}>
//         <Col>
//           <Dropdown
//             open={open}
//             onOpenChange={(flag) => {
//               setOpen(flag);
//               if (!flag) {
//                 setSearchText(""); // clear search when closed
//               }
//             }}
//             dropdownRender={() => dropdownContent}
//             trigger={["click"]}
//           >
//             <Button
//               type="primary"
//               icon={<DownOutlined />}
//               style={{
//                 background: "#14b8a6",
//                 borderColor: "#14b8a6",
//                 height: 40,
//                 fontSize: 14,
//                 fontWeight: 500,
//                 padding: "0 18px",
//               }}
//             >
//               Search & add symbol to the marketwatch
//             </Button>
//           </Dropdown>
//         </Col>
//       </Row>

//       <MarketWatchTable />
//     </div>
//   );
// };

// export default MarketWatch;