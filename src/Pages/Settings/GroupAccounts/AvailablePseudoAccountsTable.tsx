import React from "react";
import { Table, Input } from "antd";
import { SearchOutlined } from "@ant-design/icons";

const columns = [
  { title: "Add", dataIndex: "add", sorter: true },
  { title: "Pseudo Acc", dataIndex: "pseudoAcc", sorter: true },
  { title: "Trading Acc", dataIndex: "tradingAcc", sorter: true },
  { title: "Broker", dataIndex: "broker", sorter: true },
  { title: "Live", dataIndex: "live", sorter: true },
];

const AvailablePseudoAccountsTable: React.FC = () => {
  return (
    <>
      <div style={{ textAlign: "right", marginBottom: 8 }}>
        <Input
          prefix={<SearchOutlined />}
          placeholder="Search"
          style={{ width: 220 }}
        />
      </div>

      <Table
        bordered
        pagination={false}
        columns={columns}
        dataSource={[]}
        locale={{ emptyText: "" }}
        components={{
          body: {
            wrapper: () => (
              <tbody>
                <tr>
                  <td
                    colSpan={columns.length}
                    style={{
                      textAlign: "center",
                      fontWeight: "bold",
                      padding: "12px",
                      borderBottom: "1px solid #f0f0f0"
                    }}
                  >
                    No data available in table
                  </td>
                </tr>
              </tbody>
            ),
          },
        }}
      />

      <p style={{ marginTop: 8 }}>Showing 0 to 0 of 0 entries</p>
    </>
  );
};

export default AvailablePseudoAccountsTable;
