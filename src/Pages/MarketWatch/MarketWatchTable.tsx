import React, { useState, useEffect } from "react";
import { Table, Select, Button } from "antd";
import { useNavigate } from "react-router-dom";

interface Props {
  data: any[];
  liveData: Record<string, any>;
  onDelete?: (symbol: string) => void;
}

const MarketWatchTable: React.FC<Props> = ({
  data,
  liveData,
  onDelete,
}) => {
  const [filters, setFilters] = useState<{ [key: string]: string }>({});
  const [filteredData, setFilteredData] = useState<any[]>(data);
  const navigate = useNavigate();

  useEffect(() => {
    setFilteredData(data);
  }, [data]);

  const getValue = (record: any, key: string) => {
    const tick = liveData[record.symbol];
    return tick?.[key] ?? record?.[key] ?? "--";
  };

  const handleColumnFilter = (value: string, key: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);

    let tempData = [...data];

    Object.keys(newFilters).forEach((k) => {
      if (newFilters[k]) {
        tempData = tempData.filter((row: any) =>
          String(getValue(row, k))
            .toLowerCase()
            .includes(newFilters[k].toLowerCase())
        );
      }
    });

    setFilteredData(tempData);
  };

  const columns: any[] = [
    {
      key: "symbol",
      title: "Symbol",
      dataIndex: "symbol",
      sorter: (a: any, b: any) =>
        String(a.symbol).localeCompare(String(b.symbol)),
    },
    {
      key: "last_price",
      title: "LTP",
      width: 100,
      render: (_: any, record: any) => (
        <div style={{ background: "#fffbe6", textAlign: "center" }}>
          ₹{getValue(record, "last_price")}
        </div>
      ),
    },
    {
      key: "buy",
      title: "Buy",
      width: 100,
      render: (_: any, record: any) => (
        <div style={{ textAlign: "center" }}>
          <Button
            size="small"
            style={{
              background: "#52c41a",
              color: "#fff",
              border: "none",
            }}
            onClick={() =>
              navigate("/trading/trade", {
                state: {
                  symbol: record.symbol,
                  exchange: record.exchange,
                  side: "BUY",

                  price: getValue(record, "last_price"),
                  quantity: 1, // default
                  scrip_code: record.scrip_code,
                  name: record.name,
                },
              })
            }
          >
            Buy
          </Button>
          <div style={{ fontSize: 12 }}>
            ₹{getValue(record, "buy_price")}
          </div>
        </div>
      ),
    },
    {
      key: "sell",
      title: "Sell",
      width: 100,
      render: (_: any, record: any) => (
        <div style={{ textAlign: "center" }}>
          <Button
            size="small"
            danger
            onClick={() =>
              navigate("/trading/trade", {
                state: {
                  symbol: record.symbol,
                  exchange: record.exchange,
                  side: "SELL",

                  // 🔥 ADD THESE
                  price: getValue(record, "last_price"),
                  quantity: 1,
                },
              })
            }
          >
            Sell
          </Button>
          <div style={{ fontSize: 12 }}>
            ₹{getValue(record, "sell_price")}
          </div>
        </div>
      ),
    },
    {
      key: "change_percent",
      title: "% Chg",
      width: 100,
      render: (_: any, record: any) => {
        const val = getValue(record, "change_percent");
        return (
          <span style={{ color: val >= 0 ? "green" : "red" }}>
            {val >= 0 ? "+" : ""}
            {val}%
          </span>
        );
      },
    },
    {
      key: "time",
      title: "Time",
      width: 120,
      render: (_: any, record: any) =>
        getValue(record, "last_trade_time"),
    },
    {
      key: "volume",
      title: "Volume",
      width: 100,
      render: (_: any, record: any) => getValue(record, "volume"),
    },
    {
      key: "oi",
      title: "OI",
      width: 100,
      render: (_: any, record: any) => getValue(record, "oi"),
    },
    {
      key: "open",
      title: "Open",
      width: 100,
      render: (_: any, record: any) => getValue(record, "open"),
    },
    {
      key: "high",
      title: "High",
      width: 100,
      render: (_: any, record: any) => getValue(record, "high"),
    },
    {
      key: "low",
      title: "Low",
      width: 100,
      render: (_: any, record: any) => getValue(record, "low"),
    },
    {
      key: "prev_close",
      title: "Prev. Cl",
      width: 100,
      render: (_: any, record: any) => getValue(record, "prev_close"),
    },
    {
      key: "avg_price",
      title: "Avg. Prc",
      width: 100,
      render: (_: any, record: any) => getValue(record, "avg_price"),
    },
    {
      key: "ltq",
      title: "Ltq.",
      width: 100,
      render: (_: any, record: any) => getValue(record, "ltq"),
    },
    {
      key: "total_buy_qty",
      title: "Tot. B-Qty",
      width: 120,
      render: (_: any, record: any) =>
        getValue(record, "total_buy_qty"),
    },
    {
      key: "total_sell_qty",
      title: "Tot. S-Qty",
      width: 120,
      render: (_: any, record: any) =>
        getValue(record, "total_sell_qty"),
    },
    {
      key: "exchange",
      title: "Exch",
      width: 100,
      render: (_: any, record: any) => record.exchange,
    },
    {
      key: "delete",
      title: "Delete",
      width: 100,
      render: (_: any, record: any) => (
        <Button danger size="small" onClick={() => onDelete?.(record.symbol)}>
          Delete
        </Button>
      ),
    },
  ];

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
      rowKey="symbol"
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
                  <td colSpan={columns.length} style={{ textAlign: "center" }}>
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