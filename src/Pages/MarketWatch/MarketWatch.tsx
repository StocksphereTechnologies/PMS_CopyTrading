import React, { useState } from "react";
import { Button, Row, Col, Dropdown, Select } from "antd";
import { DownOutlined } from "@ant-design/icons";
import MarketWatchTable from "./MarketWatchTable";

const { Option } = Select;

const MarketWatch: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [searchText, setSearchText] = useState("");

  // Dummy symbols (replace later with API)
  const symbols: string[] = [
    "NIFTY",
    "BANKNIFTY",
    "RELIANCE",
    "TCS",
  ];

  const filteredSymbols =
    searchText.length >= 2
      ? symbols.filter((s) =>
        s.toLowerCase().includes(searchText.toLowerCase())
      )
      : [];

  const dropdownContent = (
    <div
      style={{
        background: "#fff",
        padding: 10,
        width: 300,
        boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
        borderRadius: 4,
      }}
    >
      <Select
        showSearch
        autoFocus
        placeholder="Search symbol"
        style={{ width: "100%" }}
        value={searchText || undefined}
        filterOption={false}
        onSearch={(val) => setSearchText(val)}
        notFoundContent={
          searchText.length < 2
            ? "Please enter 2 or more characters"
            : "No symbol found"
        }
      >
        {filteredSymbols.map((sym) => (
          <Option key={sym} value={sym}>
            {sym}
          </Option>
        ))}
      </Select>
    </div>
  );

  return (
    <div style={{ padding: 16 }}>
      {/* Search & Add Symbol */}
      <Row style={{ marginBottom: 12 }}>
        <Col>
          <Dropdown
            open={open}
            onOpenChange={(flag) => {
              setOpen(flag);
              if (!flag) {
                setSearchText(""); // clear search when closed
              }
            }}
            dropdownRender={() => dropdownContent}
            trigger={["click"]}
          >
            <Button
              type="primary"
              icon={<DownOutlined />}
              style={{
                background: "#14b8a6",
                borderColor: "#14b8a6",
                height: 40,
                fontSize: 14,
                fontWeight: 500,
                padding: "0 18px",
              }}
            >
              Search & add symbol to the marketwatch
            </Button>
          </Dropdown>
        </Col>
      </Row>

      <MarketWatchTable />
    </div>
  );
};

export default MarketWatch;