import React, { useState } from "react";
import { Table, Select, Button } from "antd";

const { Option } = Select;

const initialData: any[] = [];

const columns = [
  {
    key: "symbol",
    title: "Symbol",
    dataIndex: "symbol",
    sorter: (a: any, b: any) => String(a.symbol).localeCompare(String(b.symbol)),
  },
  {
    key: "ltp",
    title: "LTP",
    dataIndex: "ltp",
    width: 100,
    sorter: (a: any, b: any) => String(a.ltp).localeCompare(String(b.ltp)),
    render: (val: any) => (
      <div style={{ background: "#fffbe6", textAlign: "center" }}>
        {val}
      </div>
    ),
  },
  {
    key: "buy",
    title: "Buy",
    width: 80,
    render: () => (
      <Button size="small" style={{ background: "#52c41a", color: "#fff" }}>
        Buy
      </Button>
    ),
  },
  {
    key: "sell",
    title: "Sell",
    width: 80,
    render: () => (
      <Button danger size="small">
        Sell
      </Button>
    ),
  },
  {
    key: "percentChange",
    title: "% Chg",
    dataIndex: "percentChange",
    width: 100,
    sorter: (a: any, b: any) => a.percentChange - b.percentChange,
    render: (val: number) => (
      <span style={{ color: val >= 0 ? "green" : "red" }}>
        {val}%
      </span>
    ),
  },
  { key: "time", 
    title: "Time",
    dataIndex: "time",
    width: 120,
    sorter: (a: any, b: any) => String(a.time).localeCompare(String(b.time)),
  }, 
  { key: "volume", 
    title: "Volume", 
    dataIndex: "volume", 
    width: 100,
    sorter: (a: any, b: any) => parseInt(a.volume) - parseInt(b.volume),
  },
  { key: "oi", 
    title: "OI", 
    dataIndex: "oi", 
    width: 100,
    sorter: (a: any, b: any) => parseInt(a.oi) - parseInt(b.oi),
  },
  { key: "open", 
    title: "Open", 
    dataIndex: "open", 
    width: 100,
    sorter: (a: any, b: any) => a.open - b.open,
  },
  { key: "high", 
    title: "High", dataIndex: "high", width: 100,
    sorter: (a: any, b: any) => a.high - b.high,
  },
  { key: "low", 
    title: "Low", 
    dataIndex: "low", 
    width: 100,
    sorter: (a: any, b: any) => a.low - b.low,
  },
  { key: "prevClose", 
    title: "Prev. Cl", 
    dataIndex: "prevClose", 
    width: 100,
    sorter: (a: any, b: any) => a.prevClose - b.prevClose,
  },
  { key: "avgPrice", 
    title: "Avg. Prc", 
    dataIndex: "avgPrice", 
    width: 100,
    sorter: (a: any, b: any) => a.avgPrice - b.avgPrice,
  },
  { key: "ltq", 
    title: "Ltq.", 
    dataIndex: "ltq", 
    width: 100,
    sorter: (a: any, b: any) => a.ltq - b.ltq,
  },
  {
    key: "totalBuyQty",
    title: "Tot. B-Qty",
    dataIndex: "totalBuyQty",
    width: 120,
    sorter: (a: any, b: any) => a.totalBuyQty - b.totalBuyQty,
  },
  {
    key: "totalSellQty",
    title: "Tot. S-Qty",
    dataIndex: "totalSellQty",
    width: 120,
    sorter: (a: any, b: any) => a.totalSellQty - b.totalSellQty,
  },
  {
    key: "exch",
    title: "Exch",
    dataIndex: "exch",
    width: 120,
    sorter: (a: any, b: any) => String(a.exch).localeCompare(String(b.exch)),
  },
  {
    key: "delete",
    title: "Delete",
    width: 120,
    sorter: (a: any, b: any) => String(a.delete).localeCompare(String(b.delete)),
    render: () => <Button danger size="small">Delete</Button>,
  },
];

const MarketWatchTable: React.FC = () => {
  const [filters, setFilters] = useState<{ [key: string]: string }>({});
  const [filteredData, setFilteredData] = useState(initialData);

  // Same filter logic as Holdings
  const handleColumnFilter = (value: string, key: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);

    let data = initialData;

    Object.keys(newFilters).forEach((k) => {
      if (newFilters[k]) {
        data = data.filter((row: any) =>
          String(row[k])
            .toLowerCase()
            .includes(newFilters[k].toLowerCase())
        );
      }
    });

    setFilteredData(data);
  };

  // Filter row (same structure as Holdings)
  const filterRow = (
    <tr>
      {columns.map((col: any) => (
        <th key={col.key}>
          <Select
            allowClear
            size="small"
            style={{ width: "100%" }}
            value={filters[col.key]}
            onChange={(v) => handleColumnFilter(v || "", col.key)}
          />
        </th>
      ))}
    </tr>
  );

  return (
    <Table
      bordered
      pagination={false}
      columns={columns}
      dataSource={filteredData}
      scroll={{ x: "max-content" }}
      locale={{ emptyText: "" }}
      components={{
        header: {
          wrapper: (props: any) => (
            <thead {...props}>
              {props.children}
              {filterRow}
            </thead>
          ),
        },
        body: {
          wrapper: (props: any) =>
            filteredData.length === 0 ? (
              <tbody>
                <tr>
                  <td
                    colSpan={columns.length}
                    style={{ textAlign: "center", fontWeight: "bold" }}
                  >
                    No Data Available in table
                  </td>
                </tr>
              </tbody>
            ) : (
              <tbody {...props} />
            ),
        },
      }}
    />
  );
};

export default MarketWatchTable;