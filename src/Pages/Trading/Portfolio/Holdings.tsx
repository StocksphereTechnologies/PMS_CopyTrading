import React, { useState } from "react";
import {Input,Button,Tooltip,Row,Col,} from "antd";
import { SearchOutlined } from "@ant-design/icons";
import HoldingsTable from "./HoldingsTable";

const greyBtn = { background: "#6e6e6e", color: "#fff" };
const greenBtn = { background: "#11c26d", color: "#fff" };
const orangeBtn = { background: "#ff8c5a", color: "#fff" };

const Holdings: React.FC = () => {
  const [searchText, setSearchText] = useState("");

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={8} style={{ marginBottom: 8 }}>
        <Col><Tooltip title="Reset Holdings Filter"><Button style={greyBtn}>Reset</Button></Tooltip></Col>
        <Col><Tooltip title="Select all holdings"><Button style={greyBtn}>Select</Button></Tooltip></Col>
        <Col><Tooltip title="Deselect all holdings"><Button style={greyBtn}>Deselect</Button></Tooltip></Col>
        <Col><Tooltip title="Square-Off"><Button style={orangeBtn}>Square-Off</Button></Tooltip></Col>
        <Col><Tooltip title="Increase"><Button style={greenBtn}>Increase</Button></Tooltip></Col>

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

      <Row gutter={8} style={{ marginBottom: 12 }}>
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

      <HoldingsTable />
    </div>
  );
};

export default Holdings;
