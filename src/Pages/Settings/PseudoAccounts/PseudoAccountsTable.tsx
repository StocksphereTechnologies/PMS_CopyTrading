import React, { useState } from "react";
import { Table, Select } from "antd";

const initialData: any[] = [];

const columns = [
  { title: "Nickname", dataIndex: "nickname", sorter: true },
  { title: "Trading Acc", dataIndex: "tradingAcc", sorter: true },
  { title: "Live", dataIndex: "live", sorter: true },
  { title: "Session", dataIndex: "session", sorter: true },
  { title: "Expiry", dataIndex: "expiry", sorter: true },
  { title: "Days", dataIndex: "days", sorter: true },
  { title: "Paid", dataIndex: "paid", sorter: true },
  { title: "Broker", dataIndex: "broker", sorter: true },
  { title: "Platform", dataIndex: "platform", sorter: true },
];

const PseudoAccountsTable: React.FC<{ searchText: string }> = ({ searchText }) => {
  const [filters, setFilters] = useState<any>({});
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

    if (searchText) {
      data = data.filter((row: any) =>
        Object.values(row).some((v: any) =>
          String(v).toLowerCase().includes(searchText.toLowerCase())
        )
      );
    }

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
                    style={{
                      textAlign: "center",
                      fontWeight: "bold",
                      padding: "12px",
                      borderBottom: "1px solid #d9d9d9",
                    }}
                  >
                    No data available in table
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

export default PseudoAccountsTable;
