import React from "react";
import { Input, Row, Col, Button, InputNumber } from "antd";
import GroupPseudoAccountsTable from "./GroupPseudoAccountsTable";
import AvailablePseudoAccountsTable from "./AvailablePseudoAccountsTable";

const CreateGroupAccount: React.FC = () => {
  return (
    <div style={{ padding: 16 }}>
      <h2 style={{ color: "#0bb", marginBottom: 16 }}>Group Account</h2>

      {/* BIG CONTAINER */}
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
            <label style={{ display: "block", marginBottom: 6 }}>Name</label>
            <Input placeholder="Group Name" />
          </Col>

          <Col span={6}>
            <label style={{ display: "block", marginBottom: 6 }}>
              Qty. Multiplier{" "}
              <span style={{ color: "#1890ff" }}>[0.05 to 10000]</span>
            </label>
            <InputNumber
              min={0.05}
              max={10000}
              step={0.01}
              defaultValue={1.0}
              style={{ width: "100%" }}
            />
          </Col>

          <Col span={12}>
            <label style={{ display: "block", marginBottom: 6 }}>
              Description
            </label>
            <Input placeholder="What is this group for?" />
          </Col>
        </Row>
      </div>

      {/* TABLES */}
      <h3 style={{ color: "#fa8c16" }}>Group's Pseudo Accounts</h3>
      <GroupPseudoAccountsTable />

      <h3 style={{ color: "#52c41a", marginTop: 24 }}>
        Available Pseudo Accounts
      </h3>
      <AvailablePseudoAccountsTable />

      <Button
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
