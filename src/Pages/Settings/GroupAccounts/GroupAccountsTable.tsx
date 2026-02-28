import React, { useState } from "react";
import { Table } from "antd";

const initialData: any[] = [];

const columns = [
  {
    title: "Name",
    dataIndex: "name",
    sorter: (a: any, b: any) =>
      String(a.name).localeCompare(String(b.name)),
  },
  {
    title: "Total Accounts",
    dataIndex: "totalAccounts",
    sorter: (a: any, b: any) =>
      Number(a.totalAccounts) - Number(b.totalAccounts),
  },
  {
    title: "Multiplier",
    dataIndex: "multiplier",
    sorter: (a: any, b: any) =>
      Number(a.multiplier) - Number(b.multiplier),
  },
  {
    title: "Description",
    dataIndex: "description",
    sorter: (a: any, b: any) =>
      String(a.description).localeCompare(String(b.description)),
  },
];

const GroupAccountsTable: React.FC<{ searchText: string }> = ({ searchText }) => {
  const [data] = useState(initialData);

  const filteredData = searchText
    ? data.filter((row: any) =>
        Object.values(row).some((v: any) =>
          String(v).toLowerCase().includes(searchText.toLowerCase())
        )
      )
    : data;

  return (
    <Table
      bordered
      pagination={false}
      columns={columns}
      dataSource={filteredData}
      locale={{ emptyText: "" }}
      components={{
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

export default GroupAccountsTable;
