import React from "react";
import { Table, Tooltip } from "antd";
import { EditOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import type { ColumnsType } from "antd/es/table";

export interface GroupData {
  key: number;
  id: number;
  name: string;
  totalAccounts: number;
  multiplier: number;
  description: string;
  accounts?: any[];
}

interface Props {
  searchText: string;
  data: GroupData[];
}

const GroupName: React.FC<Props> = ({ searchText, data }) => {
  const navigate = useNavigate();

  const handleEdit = (record: GroupData) => {
    navigate(`/settings/groupaccounts/creategroupaccount/${record.id}`, {
      state: { group: record },
    });
  };

  const columns: ColumnsType<GroupData> = [
    {
      title: "Name",
      dataIndex: "name",
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: "Total Accounts",
      dataIndex: "totalAccounts",
      sorter: (a, b) => a.totalAccounts - b.totalAccounts,
    },
    {
      title: "Multiplier",
      dataIndex: "multiplier",
      sorter: (a, b) => a.multiplier - b.multiplier,
    },
    {
      title: "Description",
      dataIndex: "description",
      sorter: (a, b) => a.description.localeCompare(b.description),
    },
    {
      title: "Edit",
      key: "edit",
      align: "center",
      render: (_, record) => (
        <Tooltip title="Edit Group">
          <EditOutlined
            style={{
              color: "#1890ff",
              cursor: "pointer",
              fontSize: 18,
            }}
            onClick={() => handleEdit(record)}
          />
        </Tooltip>
      ),
    },
  ];

  const filteredData = data.filter((row) => {
    if (!searchText) return true;

    return Object.values(row)
      .join(" ")
      .toLowerCase()
      .includes(searchText.toLowerCase());
  });

  return (
    <Table
      bordered
      columns={columns}
      dataSource={filteredData}
      pagination={false}
      rowKey="key"
      locale={{ emptyText: "No data available in table" }}
    />
  );
};

export default GroupName;

// import React from "react";
// import { Table } from "antd";

// export interface GroupData {
//   key: number;
//   name: string;
//   totalAccounts: number;
//   multiplier: number;
//   description: string;
// }

// interface Props {
//   searchText: string;
//   data: GroupData[];
// }

// const GroupAccountsTable: React.FC<Props> = ({ searchText, data }) => {

//   const columns = [
//     {
//       title: "Name",
//       dataIndex: "name",
//       sorter: (a: GroupData, b: GroupData) =>
//         a.name.localeCompare(b.name),
//     },
//     {
//       title: "Total Accounts",
//       dataIndex: "totalAccounts",
//       sorter: (a: GroupData, b: GroupData) =>
//         a.totalAccounts - b.totalAccounts,
//     },
//     {
//       title: "Multiplier",
//       dataIndex: "multiplier",
//       sorter: (a: GroupData, b: GroupData) =>
//         a.multiplier - b.multiplier,
//     },
//     {
//       title: "Description",
//       dataIndex: "description",
//       sorter: (a: GroupData, b: GroupData) =>
//         a.description.localeCompare(b.description),
//     },
//   ];

//   const filteredData = searchText
//     ? data.filter((row) =>
//         Object.values(row).some((value) =>
//           String(value).toLowerCase().includes(searchText.toLowerCase())
//         )
//       )
//     : data;

//   return (
//     <Table
//       bordered
//       pagination={false}
//       columns={columns}
//       dataSource={filteredData}
//       rowKey="key"
//       locale={{ emptyText: "No data available in table" }}
//     />
//   );
// };

// export default GroupAccountsTable;


// import React, { useState } from "react";
// import { Table } from "antd";

// const initialData: any[] = [];

// const columns = [
//   {
//     title: "Name",
//     dataIndex: "name",
//     sorter: (a: any, b: any) =>
//       String(a.name).localeCompare(String(b.name)),
//   },
//   {
//     title: "Total Accounts",
//     dataIndex: "totalAccounts",
//     sorter: (a: any, b: any) =>
//       Number(a.totalAccounts) - Number(b.totalAccounts),
//   },
//   {
//     title: "Multiplier",
//     dataIndex: "multiplier",
//     sorter: (a: any, b: any) =>
//       Number(a.multiplier) - Number(b.multiplier),
//   },
//   {
//     title: "Description",
//     dataIndex: "description",
//     sorter: (a: any, b: any) =>
//       String(a.description).localeCompare(String(b.description)),
//   },
// ];

// const GroupAccountsTable: React.FC<{ searchText: string }> = ({ searchText }) => {
//   const [data] = useState(initialData);

//   const filteredData = searchText
//     ? data.filter((row: any) =>
//         Object.values(row).some((v: any) =>
//           String(v).toLowerCase().includes(searchText.toLowerCase())
//         )
//       )
//     : data;

//   return (
//     <Table
//       bordered
//       pagination={false}
//       columns={columns}
//       dataSource={filteredData}
//       locale={{ emptyText: "" }}
//       components={{
//         body: {
//           wrapper: (props: any) =>
//             filteredData.length === 0 ? (
//               <tbody>
//                 <tr>
//                   <td
//                     colSpan={columns.length}
//                     style={{
//                       textAlign: "center",
//                       fontWeight: "bold",
//                       padding: "12px",
//                       borderBottom: "1px solid #d9d9d9",
//                     }}
//                   >
//                     No data available in table
//                   </td>
//                 </tr>
//               </tbody>
//             ) : (
//               <tbody {...props} />
//             ),
//         },
//       }}
//     />
//   );
// };

// export default GroupAccountsTable;
