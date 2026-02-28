import React, { useState } from "react";
import { Button, Input, Row, Col, Tooltip } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import GroupAccountsTable from "./GroupAccountsTable";
import { useNavigate } from "react-router-dom";

const tealBtn = { background: "#0bb", color: "#fff" };

const GroupAccounts: React.FC = () => {
  const [searchText, setSearchText] = useState("");
  const navigate = useNavigate();

  return (
    <div style={{ padding: 16 }}>
      <h2>Group Accounts</h2>

      <p style={{ color: "#c45a00", marginBottom: 12 }}>
        A list of all your group accounts configured with AutoTrader
      </p>

      <Row gutter={8} style={{ marginBottom: 12 }}>
        <Col>
          <Tooltip title="Create a Trading Account.">
            <Button
              style={tealBtn}
              onClick={() =>
                navigate("/settings/groupaccounts/creategroupaccount")
              }
            >
              Create
            </Button>
          </Tooltip>
        </Col>

        <Col flex="auto" />

        <Col>
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 220 }}
          />
        </Col>
      </Row>

      <GroupAccountsTable searchText={searchText} />
    </div>
  );
};

export default GroupAccounts;
