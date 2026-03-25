import React, { useState, useEffect } from "react";
import { Button, Row, Col, Dropdown, Select } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import axios from "axios";
import MarketWatchTable from "./MarketWatchTable";

const MarketWatch: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [searchText, setSearchText] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [liveData, setLiveData] = useState<Record<string, any>>({});

  // ✅ LTP Polling
  useEffect(() => {
    if (watchlist.length === 0) return;

    const fetchLTP = async () => {
      try {
        const instruments = watchlist.map((item) => ({
          scrip_code: item.scrip_code,
          exchange: item.exchange,
          symbol: item.symbol,
          name: item.name,
        }));

        const res = await axios.post(
          "http://localhost:8000/api/v1/marketwatch/ltp",
          { instruments }
        );

        const data = res.data?.data || [];

        setLiveData((prev) => {
          const next = { ...prev };
          data.forEach((tick: any) => {
            if (tick.symbol) next[tick.symbol] = tick;
          });
          return next;
        });
      } catch (err) {
        console.error("LTP error", err);
      }
    };

    fetchLTP();
    const interval = setInterval(fetchLTP, 3000);
    return () => clearInterval(interval);
  }, [watchlist]);

  // ✅ Search
  const handleSearch = async (val: string) => {
    setSearchText(val);

    if (val.length >= 2) {
      try {
        const res = await axios.get(
          "http://localhost:8000/api/v1/marketwatch/search",
          { params: { q: val } }
        );
        setSearchResults(res.data.instruments || []);
      } catch (err) {
        console.error("Search error", err);
      }
    } else {
      setSearchResults([]);
    }
  };

  // ✅ Add
  const addToWatchlist = (item: any) => {
    setWatchlist((prev) => {
      if (prev.find((i) => i.symbol === item.symbol)) return prev;
      return [...prev, item];
    });

    setOpen(false);
    setSearchText("");
  };

  // ✅ Remove
  const removeFromWatchlist = (symbol: string) => {
    setWatchlist((prev) =>
      prev.filter((item) => item.symbol !== symbol)
    );

    setLiveData((prev) => {
      const next = { ...prev };
      delete next[symbol];
      return next;
    });
  };

  const dropdownContent = (
    <div style={{ background: "#fff", padding: 12, width: 350 }}>
      <Select
        showSearch
        autoFocus
        placeholder="Search symbol"
        style={{ width: "100%" }}
        value={searchText || undefined}
        filterOption={false}
        onSearch={handleSearch}
        dropdownStyle={{ display: "none" }}
        open={false}
      />

      <div style={{ maxHeight: 250, overflowY: "auto", marginTop: 8 }}>
        {searchResults.map((item) => (
          <div
            key={item.symbol}
            onClick={() => addToWatchlist(item)}
            style={{
              padding: 10,
              cursor: "pointer",
              borderBottom: "1px solid #f0f0f0",
            }}
          >
            <b>{item.symbol}</b> ({item.exchange}) - ₹
            {item.last_price || "--"}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div style={{ padding: 16 }}>
      <Row style={{ marginBottom: 12 }}>
        <Col>
          <Dropdown
            open={open}
            onOpenChange={setOpen}
            dropdownRender={() => dropdownContent}
            trigger={["click"]}
          >
            <Button
              type="primary"
              icon={<SearchOutlined />}
              style={{ background: "#14b8a6", borderColor: "#14b8a6" }}
            >
              Search & Add Symbol
            </Button>
          </Dropdown>
        </Col>
      </Row>

      <MarketWatchTable
        data={watchlist}
        liveData={liveData}
        onDelete={removeFromWatchlist}
      />
    </div>
  );
};

export default MarketWatch;

