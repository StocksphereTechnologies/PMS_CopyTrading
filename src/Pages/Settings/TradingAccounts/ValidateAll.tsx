import React, { useState } from "react";
import { Table, Select, Tag } from "antd";

const { Option } = Select;

const initialData: any[] = [];

const columns = [
  { title: "Login ID", dataIndex: "loginId", sorter: true },
  { title: "Nickname", dataIndex: "nickname", sorter: true },
  { title: "Live", dataIndex: "live", sorter: true },
  { title: "Session", dataIndex: "session", sorter: true },
  { title: "Message", dataIndex: "message", sorter: true },
  {
    title: "Valid",
    dataIndex: "valid",
    sorter: true,
    render: (value: string) =>
      value === "YES" ? (
        <Tag color="green">YES</Tag>
      ) : (
        <Tag color="red">NO</Tag>
      ),
  },
];

const ValidateAll: React.FC = () => {
  const [filters, setFilters] = useState<any>({});
  const [filteredData, setFilteredData] = useState(initialData);

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

  const filterRow = (
    <tr>
      {columns.map((col: any) => (
        <th key={col.dataIndex}>
          <Select
            allowClear
            size="small"
            style={{ width: "100%" }}
            value={filters[col.dataIndex]}
            onChange={(v) =>
              handleColumnFilter(v || "", col.dataIndex)
            }
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
      rowKey="loginId"
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
                        padding: "8px",
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

export default ValidateAll;
