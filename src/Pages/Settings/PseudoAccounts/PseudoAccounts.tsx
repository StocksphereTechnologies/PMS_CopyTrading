import React, { useState } from "react";
import { Button, Input, Row, Col, Tooltip } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import PseudoAccountsTable from "./PseudoAccountsTable";

const greyBtn = { background: "#7f8c8d", color: "#fff" };
const greenBtn = { background: "#2ecc71", color: "#fff" };
const orangeBtn = { background: "#f39c12", color: "#fff" };
const redBtn = { background: "#e74c3c", color: "#fff" };
const tealBtn = { background: "#0bb", color: "#fff" };

const PseudoAccounts: React.FC = () => {
  const [searchText, setSearchText] = useState("");

  return (
    <div style={{ padding: 16 }}>
      <h2>Pseudo Accounts</h2>

      <p style={{ color: "#c45a00", marginBottom: 12 }}>
        A list of all your nicknames (a.k.a. pseudo accounts) configured with AutoTrader.
        Click on the Edit icon in the first column to edit.
      </p>

      <Row gutter={8} style={{ marginBottom: 12 }}>
        <Col>
          <Tooltip title="Create a Psuedo Account.">
            <Button style={tealBtn}>Create</Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="The system will check for any login issues in all live accounts.">
            <Button style={tealBtn}>Validate All</Button>
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

      <PseudoAccountsTable searchText={searchText} />
    </div>
  );
};

export default PseudoAccounts;
