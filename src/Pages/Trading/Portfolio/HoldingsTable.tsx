import React, { useEffect, useState } from "react";
import { Table, Select } from "antd";
import { holdingsService, Holding } from "../../../Services/holdingsService";

const { Option } = Select;

const parseCurrency = (val: any) =>
  parseFloat(String(val).replace(/[^0-9.-]+/g, "")) || 0;

const columns = [
  {
    key: "pseAcc",
    title: "Pse Acc",
    dataIndex: "pseAcc",
    sorter: (a: any, b: any) => String(a.pseAcc).localeCompare(String(b.pseAcc)),
  },
  {
    key: "trdAcc",
    title: "Trd Acc",
    dataIndex: "trdAcc",
    sorter: (a: any, b: any) => String(a.trdAcc).localeCompare(String(b.trdAcc)),
  },
  {
    key: "exchange",
    title: "Exchange",
    dataIndex: "exchange",
    sorter: (a: any, b: any) => String(a.exchange).localeCompare(String(b.exchange)),
  },
  {
    key: "symbol",
    title: "Symbol",
    dataIndex: "symbol",
    sorter: (a: any, b: any) => String(a.symbol).localeCompare(String(b.symbol)),
  },
  {
    key: "totqty",
    title: "Tot Qty",
    dataIndex: "totqty",
    sorter: (a: any, b: any) => parseCurrency(a.totqty) - parseCurrency(b.totqty),
  },
  {
    key: "ltp",
    title: "LTP",
    dataIndex: "ltp",
    render: (val: number) => `₹${val.toFixed(2)}`,
    sorter: (a: any, b: any) => Number(a.ltp) - Number(b.ltp)
  },
  {
    key: "currval",
    title: "Curr Val",
    dataIndex: "currval",
    render: (val: number) => `₹${val.toFixed(2)}`,
    sorter: (a: any, b: any) => Number(a.currval) - Number(b.currval)
  },
  {
    key: "quantity",
    title: "Quantity",
    dataIndex: "quantity",
    sorter: (a: any, b: any) => parseCurrency(a.quantity) - parseCurrency(b.quantity),
  },
  {
    key: "t1qty",
    title: "T1 Qty",
    dataIndex: "t1qty",
    sorter: (a: any, b: any) => parseCurrency(a.t1qty) - parseCurrency(b.t1qty),
  },
  {
    key: "pnl",
    title: "PnL",
    dataIndex: "pnl",
    render: (val: number) => (
      <span style={{ color: val >= 0 ? "green" : "red", fontWeight: 600 }}>
        {val.toFixed(2)}
      </span>
    ),
    sorter: (a: any, b: any) => Number(a.pnl) - Number(b.pnl)
  },
  {
    key: "product",
    title: "Product",
    dataIndex: "product",
    sorter: (a: any, b: any) => String(a.product).localeCompare(String(b.product)),
  },
  {
    key: "nsesymbol",
    title: "NSE-Symbol",
    dataIndex: "nsesymbol",
    sorter: (a: any, b: any) => String(a.nsesymbol).localeCompare(String(b.nsesymbol)),
  },
  {
    key: "bsesymbol",
    title: "BSE-Symbol",
    dataIndex: "bsesymbol",
    sorter: (a: any, b: any) => String(a.bsesymbol).localeCompare(String(b.bsesymbol)),
  },
  {
    key: "isin",
    title: "ISIN",
    dataIndex: "isin",
    sorter: (a: any, b: any) => String(a.isin).localeCompare(String(b.isin)),
  },
  {
    key: "insttoken",
    title: "Inst Token",
    dataIndex: "insttoken",
    sorter: (a: any, b: any) => String(a.insttoken).localeCompare(String(b.insttoken)),
  },
  {
    key: "collateralQty",
    title: "Collateral Qty",
    dataIndex: "collateralQty",
    sorter: (a: any, b: any) => parseCurrency(a.collateralQty) - parseCurrency(b.collateralQty),
  },
  {
    key: "collateralType",
    title: "Collateral Type",
    dataIndex: "collateralType",
    sorter: (a: any, b: any) => String(a.collateralType).localeCompare(String(b.collateralType)),
  },
  {
    key: "haircut",
    title: "Haircut",
    dataIndex: "haircut",
    sorter: (a: any, b: any) => String(a.haircut).localeCompare(String(b.haircut)),
  },
  {
    key: "avgPrice",
    title: "Avg Price",
    dataIndex: "avgPrice",
    sorter: (a: any, b: any) => Number(a.avgPrice) - Number(b.avgPrice)
  },

  {
    key: "day",
    title: "Day",
    dataIndex: "day",
    sorter: (a: any, b: any) => String(a.day).localeCompare(String(b.day)),
  },
  {
    key: "platform",
    title: "Platform",
    dataIndex: "platform",
    sorter: (a: any, b: any) => String(a.platform).localeCompare(String(b.platform)),
  },
  {
    key: "broker",
    title: "Broker",
    dataIndex: "broker",
    sorter: (a: any, b: any) => String(a.broker).localeCompare(String(b.broker)),
  },
];

const HoldingsTable: React.FC<any> = ({
  searchText,
  setFilteredData,
  selectedRowKeys,
  setSelectedRowKeys,
}) => {
  const [data, setData] = useState<Holding[]>([]);
  const [filters, setFilters] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(false);
  const [localFilteredData, setLocalFilteredData] = useState<Holding[]>([]);

  const fetchHoldings = async () => {
    try {
      setLoading(true);
      const res = await holdingsService.getAll();
      setData(res.holdings || []);
    } catch (err) {
      console.error("Holdings fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHoldings();
  }, []);

  useEffect(() => {
    let temp = data;

    // 🔍 SEARCH
    if (searchText) {
      const words = searchText.toLowerCase().split(" ");
      temp = temp.filter((row: any) =>
        words.every((word: string) => Object.values(row).some((val) =>
          String(val).toLowerCase().includes(word)
        )
        )
      );
    }

    // 🔽 COLUMN FILTER
    Object.keys(filters).forEach((k) => {
      if (filters[k]) {
        temp = temp.filter((row: any) =>
          String(row[k]).toLowerCase().includes(filters[k].toLowerCase())
        );
      }
    });

    setLocalFilteredData(temp);
    setFilteredData(temp); // 🔥 VERY IMPORTANT (for parent buttons)
  }, [data, filters, searchText]);

  const handleColumnFilter = (value: string, key: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);

    let temp = data;

    Object.keys(newFilters).forEach((k) => {
      if (newFilters[k]) {
        temp = temp.filter((row: any) =>
          String(row[k]).toLowerCase().includes(newFilters[k].toLowerCase())
        );
      }
    });

    setLocalFilteredData(temp);
    setFilteredData(temp);
  };

  const filterRow = (
    <tr>
      {columns.map((col: any) => (
        <th key={col.dataIndex}>
          <Select
            showSearch
            allowClear
            size="small"
            style={{ width: "100%" }}
            value={filters[col.dataIndex]}
            onChange={(v) => handleColumnFilter(v || "", col.dataIndex)}
          />
        </th>
      ))}
    </tr>
  );

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => {
      setSelectedRowKeys(keys);
    },
  };

  return (
    <Table
      bordered
      rowKey={(record) => record.insttoken || record.symbol}
      pagination={false}
      loading={loading}
      columns={columns}
      rowSelection={rowSelection}
      dataSource={localFilteredData}
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
            localFilteredData.length === 0 ? (
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
export const holdingsColumns = columns;
export default HoldingsTable;
