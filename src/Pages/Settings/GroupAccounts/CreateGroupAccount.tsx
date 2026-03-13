import React, { useState } from "react";
import { Input, Row, Col, Button, InputNumber, message } from "antd";
import GroupPseudoAccountsTable from "./GroupPseudoAccountsTable";
import AvailablePseudoAccountsTable from "./AvailablePseudoAccountsTable";
import { useNavigate } from "react-router-dom";

interface TableData {
  key: number;
  account_id: number;
  pseudoAcc: string;
  tradingAcc: string;
  broker: string;
  live: string;
}

interface GroupData {
  key: number;
  name: string;
  totalAccounts: number;
  multiplier: number;
  description: string;
}

const CreateGroupAccount: React.FC = () => {
  const [groupAccounts, setGroupAccounts] = useState<TableData[]>([]);
  const [groupName, setGroupName] = useState("");
  const [multiplier, setMultiplier] = useState<number>(1);
  const [description, setDescription] = useState("");

  const navigate = useNavigate();

  const handleAddAccount = (account: TableData) => {
    const exists = groupAccounts.find(
      (a) => a.account_id === account.account_id
    );

    if (!exists) {
      setGroupAccounts([...groupAccounts, account]);
    }
  };

  const handleRemoveAccount = (accountId: number) => {
    setGroupAccounts(
      groupAccounts.filter((a) => a.account_id !== accountId)
    );
  };

  const handleSaveGroup = () => {
  if (!groupName) {
    message.warning("Please enter group name");
    return;
  }

  const newGroup: GroupData = {
    key: Date.now(),
    name: groupName,
    totalAccounts: groupAccounts.length,
    multiplier: multiplier,
    description: description,
  };

  const storedGroups = localStorage.getItem("groups");

  const groups = storedGroups ? JSON.parse(storedGroups) : [];

  groups.push(newGroup);

  localStorage.setItem("groups", JSON.stringify(groups));

  message.success("Group created successfully");

  navigate("/settings/groupaccounts");
};

  return (
    <div style={{ padding: 16 }}>
      <h2 style={{ color: "#0bb", marginBottom: 16 }}>Group Account</h2>

      <div
        style={{
          border: "1px solid #d9d9d9",
          borderRadius: 4,
          padding: 20,
          marginBottom: 24,
        }}
      >
        <Row gutter={16}>
          <Col span={6}>
            <label>Name</label>
            <Input
              placeholder="Group Name"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
            />
          </Col>

          <Col span={6}>
            <label>
              Qty. Multiplier{" "}
              <span style={{ color: "#1890ff" }}>[0.05 to 10000]</span>
            </label>

            <InputNumber
              min={0.05}
              max={10000}
              step={0.01}
              value={multiplier}
              onChange={(v) => setMultiplier(Number(v))}
              style={{ width: "100%" }}
            />
          </Col>

          <Col span={12}>
            <label>Description</label>
            <Input
              placeholder="What is this group for?"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Col>
        </Row>
      </div>

      <h3 style={{ color: "#fa8c16" }}>Group's Pseudo Accounts</h3>

      <GroupPseudoAccountsTable
        accounts={groupAccounts}
        onRemoveAccount={handleRemoveAccount}
      />

      <h3 style={{ color: "#52c41a", marginTop: 24 }}>
        Available Pseudo Accounts
      </h3>

      <AvailablePseudoAccountsTable onAddAccount={handleAddAccount} />

      <Button
        onClick={handleSaveGroup}
        style={{
          background: "#0bb",
          color: "#fff",
          marginTop: 16,
        }}
      >
        Save
      </Button>
    </div>
  );
};

export default CreateGroupAccount;

// import React from "react";
// import { Input, Row, Col, Button, InputNumber } from "antd";
// import GroupPseudoAccountsTable from "./GroupPseudoAccountsTable";
// import AvailablePseudoAccountsTable from "./AvailablePseudoAccountsTable";

// const CreateGroupAccount: React.FC = () => {
//   return (
//     <div style={{ padding: 16 }}>
//       <h2 style={{ color: "#0bb", marginBottom: 16 }}>Group Account</h2>

//       {/* BIG CONTAINER */}
//       <div
//         style={{
//           border: "1px solid #d9d9d9",
//           borderRadius: 4,
//           padding: 20,
//           marginBottom: 24,
//         }}
//       >
//         <Row gutter={16}>
//           <Col span={6}>
//             <label style={{ display: "block", marginBottom: 6 }}>Name</label>
//             <Input placeholder="Group Name" />
//           </Col>

//           <Col span={6}>
//             <label style={{ display: "block", marginBottom: 6 }}>
//               Qty. Multiplier{" "}
//               <span style={{ color: "#1890ff" }}>[0.05 to 10000]</span>
//             </label>
//             <InputNumber
//               min={0.05}
//               max={10000}
//               step={0.01}
//               defaultValue={1.0}
//               style={{ width: "100%" }}
//             />
//           </Col>

//           <Col span={12}>
//             <label style={{ display: "block", marginBottom: 6 }}>
//               Description
//             </label>
//             <Input placeholder="What is this group for?" />
//           </Col>
//         </Row>
//       </div>

//       {/* TABLES */}
//       <h3 style={{ color: "#fa8c16" }}>Group's Pseudo Accounts</h3>
//       <GroupPseudoAccountsTable />

//       <h3 style={{ color: "#52c41a", marginTop: 24 }}>
//         Available Pseudo Accounts
//       </h3>
//       <AvailablePseudoAccountsTable />

//       <Button
//         style={{
//           background: "#0bb",
//           color: "#fff",
//           marginTop: 16,
//         }}
//       >
//         Save
//       </Button>
//     </div>
//   );
// };

// export default CreateGroupAccount;
