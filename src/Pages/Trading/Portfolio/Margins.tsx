import React, { useState, useEffect } from "react";
import { Input, Button, Tooltip, Row, Col, message } from "antd";
import { SearchOutlined, ReloadOutlined } from "@ant-design/icons";
import MarginsTable from "./MarginsTable";
import { marginService, AccountMargin } from "../../../Services/marginService";

const greyBtn = { background: "#6e6e6e", color: "#fff" };
const greenBtn = { background: "#11c26d", color: "#fff" };

type SegmentFilter = "all" | "equity" | "commodity";

const Margins: React.FC = () => {
  const [searchText, setSearchText] = useState("");
  const [margins, setMargins] = useState<AccountMargin[]>([]);
  const [loading, setLoading] = useState(false);
  const [segmentFilter, setSegmentFilter] = useState<SegmentFilter>("all");

  const fetchMargins = async () => {
    try {
      setLoading(true);
      const response = await marginService.getAll();
      setMargins(response.margins);
    } catch (error: any) {
      message.error(error.response?.data?.detail || "Failed to fetch margins");
      console.error("Error fetching margins:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMargins();
  }, []);

  const handleReset = () => {
    setSegmentFilter("all");
    setSearchText("");
  };

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={8} style={{ marginBottom: 8 }}>
        <Col>
          <Tooltip title="Reset Margins Filter">
            <Button style={greyBtn} onClick={handleReset}>
              Reset
            </Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Show Equity Margins">
            <Button
              style={segmentFilter === "equity" ? greenBtn : greyBtn}
              onClick={() => setSegmentFilter("equity")}
            >
              Equity
            </Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Show Commodity Margins">
            <Button
              style={segmentFilter === "commodity" ? greenBtn : greyBtn}
              onClick={() => setSegmentFilter("commodity")}
            >
              Commodity
            </Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Show Combined Margins">
            <Button
              style={segmentFilter === "all" ? greenBtn : greyBtn}
              onClick={() => setSegmentFilter("all")}
            >
              Total
            </Button>
          </Tooltip>
        </Col>
        <Col>
          <Tooltip title="Refresh Margins">
            <Button icon={<ReloadOutlined />} onClick={fetchMargins} loading={loading}>
              Refresh
            </Button>
          </Tooltip>
        </Col>
        <Col flex="auto" />
        <Col>
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search by account or broker"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 250 }}
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
          <Tooltip title="Download in CSV format">
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

      <MarginsTable
        margins={margins}
        loading={loading}
        searchText={searchText}
        segmentFilter={segmentFilter}
      />
    </div>
  );
};

export default Margins;
