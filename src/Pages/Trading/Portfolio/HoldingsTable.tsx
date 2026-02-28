import React, { useState } from "react";
import { Table, Select } from "antd";

const { Option } = Select;

const initialData: any[] = [];

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
    sorter: (a: any, b: any) =>String(a.trdAcc).localeCompare(String(b.trdAcc)),
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
    sorter: (a: any, b: any) => String(a.ltp).localeCompare(String(b.ltp)),
  },
  {
    key: "currval",
    title: "Curr Val",
    dataIndex: "currval",
    sorter: (a: any, b: any) => String(a.currval).localeCompare(String(b.currval)),
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
    sorter: (a: any, b: any) => String(a.pnl).localeCompare(String(b.pnl)),
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
    sorter: (a: any, b: any) => String(a.avgPrice).localeCompare(String(b.avgPrice)),
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


const HoldingsTable: React.FC = () => {
  const [filters, setFilters] = useState<{ [key: string]: string }>({});
  const [filteredData, setFilteredData] = useState(initialData);

  const handleColumnFilter = (value: string, key: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);

    let data = initialData;
    Object.keys(newFilters).forEach((k) => {
      if (newFilters[k]) {
        data = data.filter((row: any) =>
          String(row[k]).toLowerCase().includes(newFilters[k].toLowerCase())
        );
      }
    });

    setFilteredData(data);
  };

  const filterRow = (
    <tr>
      {columns.map((col: any) => (
        <th key={col.dataIndex}>
          <Select
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

export default HoldingsTable;
