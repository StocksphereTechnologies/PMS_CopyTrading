import React, { useState } from "react";
import {
  Input,
  Button,
  Select,
  Row,
  Col,
  Tooltip,
  Space,
} from "antd";
import { SearchOutlined } from "@ant-design/icons";

import OrdersTable from "./OrdersTable";
import OrdersSummaryCount from "./OrdersSummaryCount";
import OrdersSummaryQuantity from "./OrdersSummaryQuantity";

const { Option } = Select;

const Orders: React.FC = () => {
  const initialData: any[] = [];

  const [searchText, setSearchText] = useState("");
  const [filteredData, setFilteredData] = useState(initialData);
  const [filters, setFilters] = useState<{ [key: string]: string }>({});

  const handleSearch = (value: string) => {
    setSearchText(value);
    const lower = value.toLowerCase();

    if (!value.trim()) {
      setFilteredData(initialData);
      return;
    }

    setFilteredData(
      initialData.filter((item) =>
        Object.values(item).some((v) =>
          String(v).toLowerCase().includes(lower)
        )
      )
    );
  };

  const handleColumnFilter = (value: string, dataIndex: string) => {
    const newFilters = { ...filters, [dataIndex]: value };
    setFilters(newFilters);

    let updated = initialData;
    Object.keys(newFilters).forEach((key) => {
      if (newFilters[key]) {
        updated = updated.filter((item) =>
          String(item[key]).toLowerCase().includes(newFilters[key].toLowerCase())
        );
      }
    });

    setFilteredData(updated);
  };

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={[8, 8]} align="middle">
        <Col>
          <Tooltip title="Order Status">
            <Select defaultValue="ALL" style={{ width: 160 }}>
              <Option value="ALL">ALL</Option>
              <Option value="OPEN">OPEN</Option>
              <Option value="COMPLETE">COMPLETE</Option>
              <Option value="CANCELLED">CANCELLED</Option>
              <Option value="REJECTED">REJECTED</Option>
            </Select>
          </Tooltip>
        </Col>

        {[
          { title: "Active", color: "#00b96b" },
          { title: "Inactive", color: "#00b96b" },
          { title: "Reset", color: "#6e6e6e" },
          { title: "Select", color: "#6e6e6e" },
          { title: "Deselect", color: "#6e6e6e" },
          { title: "Modify", color: "#ea9845e9", border: "#ea7e45" },
          { title: "Cancel", color: "#fa0801", border: "#fa0801" }
        ].map((btn, idx) => (
          <Col key={idx}>
            <Tooltip title={btn.title}>
              <Button
                style={{
                  minWidth: 100,
                  backgroundColor: btn.color,
                  borderColor: btn.border || btn.color,
                  color: "#fff"
                }}
              >
                {btn.title}
              </Button>
            </Tooltip>
          </Col>
        ))}

        <Col flex="auto" />

        <Col>
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search"
            style={{ width: 200 }}
            value={searchText}
            onChange={(e) => handleSearch(e.target.value)}
          />
        </Col>
      </Row>

      <Row style={{ margin: "12px 0" }}>
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

      <OrdersTable/>
      <OrdersSummaryCount />
      <OrdersSummaryQuantity />
    </div>
  );
};

export default Orders;
