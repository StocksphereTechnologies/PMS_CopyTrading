import React from "react";
import { Table, Input, Button, Tag } from "antd";
import {
  SearchOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from "@ant-design/icons";

interface TableData {
  key: number;
  account_id: number;
  nickname: string;
  tradingAcc: string;
  broker: string;
  live: string;
}

interface Props {
  accounts: TableData[];
  onRemoveAccount: (accountId: number) => void;
}

const GroupAccountsTable: React.FC<Props> = ({
  accounts,
  onRemoveAccount,
  }) => {
  const columns = [
    {
      title: "Remove",
      key: "remove",
      render: (_: any, record: TableData) => (
        <Button
          danger
          size="small"
          icon={<DeleteOutlined />}
          onClick={() => onRemoveAccount(record.account_id)}
        >
          Remove
        </Button>
      ),
    },
    {
      title: "Nickname",
      dataIndex: "nickname",
    },
    {
      title: "Trading Acc",
      dataIndex: "tradingAcc",
    },
    {
      title: "Broker",
      dataIndex: "broker",
    },
    {
      title: "Live",
      dataIndex: "live",
      render: (live: string) => (
        <Tag color={live === "Yes" ? "green" : "orange"}>
          {live === "Yes" ? <CheckCircleOutlined /> : <CloseCircleOutlined />}{" "}
          {live}
        </Tag>
      ),
    },
  ];

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
        pagination={{ pageSize: 10 }}
        columns={columns}
        dataSource={accounts}
        rowKey="account_id"
        locale={{ emptyText: "No accounts added to group" }}
      />

      <p style={{ marginTop: 8 }}>
        Showing {accounts.length} entries
      </p>
    </>
  );
};

export default GroupAccountsTable;


// import React from "react";
// import { Table, Input } from "antd";
// import { SearchOutlined } from "@ant-design/icons";

// const columns = [
//   { title: "Remove", dataIndex: "remove", sorter: true },
//   { title: "Pseudo Acc", dataIndex: "pseudoAcc", sorter: true },
//   { title: "Trading Acc", dataIndex: "tradingAcc", sorter: true },
//   { title: "Broker", dataIndex: "broker", sorter: true },
//   { title: "Live", dataIndex: "live", sorter: true },
// ];

// const GroupPseudoAccountsTable: React.FC = () => {
//   return (
//     <>
//       <div style={{ textAlign: "right", marginBottom: 8 }}>
//         <Input
//           prefix={<SearchOutlined />}
//           placeholder="Search"
//           style={{ width: 220 }}
//         />
//       </div>

//       <Table
//         bordered
//         pagination={false}
//         columns={columns}
//         dataSource={[]}
//         locale={{ emptyText: "" }}
//         components={{
//           body: {
//             wrapper: () => (
//               <tbody>
//                 <tr>
//                   <td
//                     colSpan={columns.length}
//                     style={{
//                       textAlign: "center",
//                       fontWeight: "bold",
//                       padding: 12,
//                       borderBottom: "1px solid #f0f0f0",
//                     }}
//                   >
//                     No data available in table
//                   </td>
//                 </tr>
//               </tbody>
//             ),
//           },
//         }}
//       />

//       <p style={{ marginTop: 8 }}>Showing 0 to 0 of 0 entries</p>
//     </>
//   );
// };

// export default GroupPseudoAccountsTable;
