import React, { useState } from "react";
import { Button, Input, Row, Col, Tooltip } from "antd";
import { useNavigate } from "react-router-dom";
import type { ColumnsType } from "antd/es/table";
import { SearchOutlined } from "@ant-design/icons";
import TradingAccountsTable from "./TradingAccountsTable";
import ValidateAll from "./ValidateAll";

const greyBtn = { background: "#7f8c8d", color: "#fff" };
const greenBtn = { background: "#2ecc71", color: "#fff" };
const orangeBtn = { background: "#f39c12", color: "#fff" };
const redBtn = { background: "#e74c3c", color: "#fff" };
const darkBtn = { background: "#2f2f2f", color: "#fff" };
const tealBtn = { background: "#0bb", color: "#fff" };

const TradingAccounts: React.FC = () => {
  const [searchText, setSearchText] = useState("");
  const [viewMode, setViewMode] = useState("LIST");
  const navigate = useNavigate();

  return (
    <div style={{ padding: 16 }}>
      <h2>Trading Accounts</h2>

      <p style={{ color: "#c45a00", marginBottom: 12 }}>
        A list of all your trading accounts configured with AutoTrader.
        Click on the Edit icon in the first column to edit your credentials.
      </p>

      <Row gutter={8} style={{ marginBottom: 12 }}>
        <Col>
          <Tooltip title="Create a Trading Account.">
            <Button
              style={tealBtn}
              onClick={() =>
                navigate("/settings/tradingaccounts/createtradingaccount")
              }
            >
              Create
            </Button>
          </Tooltip>
        </Col>
        
        <Col>
          <Tooltip title="The system will check for any login issues in all live accounts.">
            <Button
              style={tealBtn}
              onClick={() => setViewMode("VALIDATE")}
              >
              Validate All
            </Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Mark selected accounts as live.">
            <Button style={greenBtn}>Live</Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Mark selected accounts as non-live.">
            <Button style={orangeBtn}>Non-Live</Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Delete selected accounts.">
            <Button style={redBtn}>Delete</Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Recharge for 31 days.">
            <Button style={darkBtn}>Recharge</Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Reset table filters.">
            <Button style={greyBtn}>Reset</Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Select all (filtered) rows.">
            <Button style={greyBtn}>Select</Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Deselect all rows.">
            <Button style={greyBtn}>Deselect</Button>
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

      {viewMode === "LIST" && (
        <TradingAccountsTable searchText={searchText} />
      )}

      {viewMode === "VALIDATE" && <ValidateAll />}
      
    </div>
  );
};

export default TradingAccounts;
