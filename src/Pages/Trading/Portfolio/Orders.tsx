import React, { useState, useEffect } from "react";
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
import { orderService, Order } from "../../../Services/orderService";

const { Option } = Select;

const Orders: React.FC = () => {
  const [searchText, setSearchText] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  const filteredOrders = orders
    .filter((order) => {

      if (statusFilter === "ALL") return true;

      const status = order.status?.toUpperCase();

      if (statusFilter === "OPEN") {
        return status === "OPEN" || status === "PENDING";
      }

      if (statusFilter === "COMPLETE") {
        return status === "COMPLETE" || status === "EXECUTED";
      }

      if (statusFilter === "CANCELLED") {
        return status === "CANCELLED";
      }

      if (statusFilter === "REJECTED") {
        return status === "REJECTED";
      }

      return true;
    })
    .filter((order) => {

      if (!searchText) return true;

      const text = searchText.toLowerCase();

      return (
        order.symbol?.toLowerCase().includes(text) ||
        order.trdAcc?.toLowerCase().includes(text) ||
        order.pseAcc?.toLowerCase().includes(text) ||
        order.status?.toLowerCase().includes(text) ||
        order.id?.toString().includes(text)
      );
    });

  const fetchOrders = async () => {
    try {
      setLoading(true);

      const response = await orderService.getAll();

      setOrders(response.orders);

    } catch (error) {
      console.error("Error fetching orders:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleResetFilters = () => {
    setStatusFilter("ALL");
    setSearchText("");
    setSelectedRowKeys([]);
  };

  const handleSelectAll = () => {
    const keys = filteredOrders.map((order) => order.id);
    setSelectedRowKeys(keys);
  };

  const handleDeselectAll = () => {
    setSelectedRowKeys([]);
  };

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={[8, 8]} align="middle">
        <Col>
          <Tooltip title="Order Status">
            <Select
              value={statusFilter}
              style={{ width: 160 }}
              onChange={(value) => setStatusFilter(value)}
            >
              <Option value="ALL">ALL</Option>
              <Option value="OPEN">OPEN</Option>
              <Option value="COMPLETE">COMPLETE</Option>
              <Option value="CANCELLED">CANCELLED</Option>
              <Option value="REJECTED">REJECTED</Option>
            </Select>
          </Tooltip>
        </Col>

        {[
          {
            title: "Reset",
            tooltip: "Reset Order filters",
            color: "#6e6e6e"
          },
          {
            title: "Select",
            tooltip: "Select all orders (if table is filtered, only filtered orders will be selected)",
            color: "#6e6e6e"
          },
          {
            title: "Deselect",
            tooltip: "Deselect all orders",
            color: "#6e6e6e"
          },
          {
            title: "Modify",
            tooltip: "Modify one or more orders with a single click",
            color: "#ea9845e9",
            border: "#ea7e45"
          },
          {
            title: "Cancel",
            tooltip: "Cancel one or more orders with a single click",
            color: "#fa0801",
            border: "#fa0801"
          }
        ].map((btn, idx) => (
          <Col key={idx}>
            <Tooltip title={btn.tooltip}>
              <Button
                onClick={() => {
                  if (btn.title === "Reset") handleResetFilters();
                  if (btn.title === "Select") handleSelectAll();
                  if (btn.title === "Deselect") handleDeselectAll();
                }}
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
            allowClear
            prefix={<SearchOutlined />}
            placeholder="Search"
            style={{ width: 200 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
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

      <OrdersTable
        orders={filteredOrders}
        loading={loading}
        selectedRowKeys={selectedRowKeys}
        setSelectedRowKeys={setSelectedRowKeys}
      />
      <OrdersSummaryCount />
      <OrdersSummaryQuantity />
    </div >
  );
};

export default Orders;
