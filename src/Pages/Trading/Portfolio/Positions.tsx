import React, { useEffect, useState } from "react";
import { Table, Input, Button, Select, Row, Col, Card, Tooltip } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import PositionSummary from "./PositionSummary";
import PositionTable from "./PositionTable";

const { Option } = Select;


const greyBtn = { background: "#6e6e6e", color: "#fff" };
const orangeBtn = { background: "#ff8c5a", color: "#fff" };

const Positions: React.FC = () => {
  const [positions, setPositions] = useState<any[]>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [searchText, setSearchText] = useState("");
  const [netType, setNetType] = useState("NET");
  const [openType, setOpenType] = useState("ALL");
  const [positionType, setPositionType] = useState("ALL");  

  const parseCurrency = (val: any) =>
    parseFloat(String(val).replace(/[^0-9.-]+/g, "")) || 0;


  const handleReset = () => {
    setNetType("NET");
    setOpenType("ALL");
    setPositionType("ALL");
    setSearchText("");
  };
  const handleSelect = () => {
  setSelectedRowKeys(
    positions
      .filter(p => p.symbol?.toLowerCase().includes(searchText.toLowerCase()))
      .map((p, i) => p.id || i)
  );
};
  return (
    <div style={{ padding: 24 }}>
      <Row gutter={10} align="middle" style={{ marginBottom: 10 }}>
        <Col>
          <Tooltip title="Category Of Positions (Keep it NET, if you are not sure)">
            <Select value={netType} style={{ width: 90 }} onChange={setNetType}>
              <Option value="DAY">DAY</Option>
              <Option value="NET">NET</Option>
            </Select>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Position State">
            <Select
              value={openType}
              style={{ width: 100 }}
              onChange={setOpenType}
            >
              <Option value="ALL">ALL</Option>
              <Option value="OPEN">OPEN</Option>
              <Option value="CLOSED">CLOSED</Option>
            </Select>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Position Direction">
            <Select
              value={positionType}
              style={{ width: 110 }}
              onChange={setPositionType}
            >
              <Option value="ALL">ALL</Option>
              <Option value="LONG">LONG</Option>
              <Option value="SHORT">SHORT</Option>
              <Option value="NEUTRAL">NEUTRAL</Option>
            </Select>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Reset position filters">
            <Button style={greyBtn} onClick={handleReset}>Reset</Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Select all positions (if filtered, only filtered positions will be selected)">
            <Button style={greyBtn} onClick={handleSelect}>
              Select
            </Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Deselect all positions">
            <Button style={greyBtn} onClick={() => setSelectedRowKeys([])}>
              Deselect
            </Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Square-Off one or more positions at market rate!">
            <Button style={orangeBtn}>Sq. Pos. Mkt.</Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Square-Off with custom options (useful when normal square-off fails!)">
            <Button style={orangeBtn}>Sq. Pos.</Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Square-Off one or more accounts (portfolios) with a single click!">
            <Button style={orangeBtn}>Sq. Acc.</Button>
          </Tooltip>
        </Col>

        <Col flex="auto" />

        <Col>
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 200 }}
          />
        </Col>
      </Row>

      <Row gutter={8} style={{ marginBottom: 8 }}>
        <Col>
          <Tooltip title="Download in Excel format">
            <Button
              style={{
                fontWeight: "bold",
                backgroundColor: "#36454F",
                color: "#fff",
              }}
            >
              Excel
            </Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Download in Csv format">
            <Button
              style={{
                fontWeight: "bold",
                backgroundColor: "#36454F",
                color: "#fff",
              }}
            >
              CSV
            </Button>
          </Tooltip>
        </Col>
      </Row>
      <PositionTable 
        setPositions={setPositions} 
        searchText={searchText} 
        openOnly={openType === "OPEN"} 
      />
      <PositionSummary positions={positions} />
    </div>
  );
};

export default Positions;
