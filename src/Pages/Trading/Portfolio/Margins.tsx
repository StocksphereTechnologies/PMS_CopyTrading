import React, { useState, useEffect } from "react";
import { Input, Button, Tooltip, Row, Col, message } from "antd";
import { SearchOutlined, ReloadOutlined } from "@ant-design/icons";
import MarginsTable from "./MarginsTable";
import { marginService, AccountMargin } from "../../../Services/marginService";
import * as XLSX from "xlsx-js-style";
import { saveAs } from "file-saver";
import { marginColumns } from "./MarginsTable";

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

  const getExportData = () => {
    const rows: any[] = [];

    margins.forEach((margin) => {
      const matchesSearch =
        !searchText ||
        margin.trading_login_id.toLowerCase().includes(searchText.toLowerCase()) ||
        margin.broker_name.toLowerCase().includes(searchText.toLowerCase()) ||
        (margin.nickname && margin.nickname.toLowerCase().includes(searchText.toLowerCase()));

      if (!matchesSearch) return;

      if ((segmentFilter === "all" || segmentFilter === "equity") && margin.equity) {
        const equity = margin.equity;
        rows.push({
          pseAcc: margin.nickname || "",
          trdAcc: margin.trading_login_id,
          category: "EQUITY",

          total: equity.available.opening_balance,
          net: equity.net,
          funds: equity.available.cash,
          utilized: equity.utilised.debits + equity.utilised.span + equity.utilised.exposure,
          available: equity.available.live_balance,
          collateral: equity.available.collateral,
          realmtm: equity.utilised.m2m_realised,
          unrealmtm: equity.utilised.m2m_unrealised,
          adhoc: equity.available.adhoc_margin,
          span: equity.utilised.span,
          exposure: equity.utilised.exposure,
          payin: equity.available.intraday_payin,
          payout: equity.utilised.payout,

          day: new Date(margin.last_updated).toISOString(), // ✅ SAFE
          broker: margin.broker_name,
        });
      }

      if ((segmentFilter === "all" || segmentFilter === "commodity") && margin.commodity) {
        const commodity = margin.commodity;
        rows.push({
          pseAcc: margin.nickname || "",
          trdAcc: margin.trading_login_id,
          category: "COMMODITY",
          total: commodity.available.opening_balance,
          net: commodity.net,
          funds: commodity.available.cash,
          utilized: commodity.utilised.debits + commodity.utilised.span + commodity.utilised.exposure,
          available: commodity.available.live_balance,
          collateral: commodity.available.collateral,
          realmtm: commodity.utilised.m2m_realised,
          unrealmtm: commodity.utilised.m2m_unrealised,
          adhoc: commodity.available.adhoc_margin,
          span: commodity.utilised.span,
          exposure: commodity.utilised.exposure,
          payin: commodity.available.intraday_payin,
          payout: commodity.utilised.payout,
          day: new Date(margin.last_updated).toISOString(), // ✅ SAFE
          broker: margin.broker_name,
        });
      }
    });

    return rows;
  };

  // ✅ EXCEL DOWNLOAD
  const handleExportExcel = () => {
    const data = getExportData();

    const headers = (marginColumns as any[])
      .map((col: any) => col.dataIndex)
      .filter(Boolean);

    const worksheet = XLSX.utils.json_to_sheet(data || [], {
      header: headers,
      skipHeader: false,
    });

    // ✅ Bold header
    headers.forEach((_, index) => {
      const cellAddress = XLSX.utils.encode_cell({ r: 0, c: index });
      if (worksheet[cellAddress]) {
        worksheet[cellAddress].s = {
          font: { bold: true },
        };
      }
    });

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Margins");

    const excelBuffer = XLSX.write(workbook, {
      bookType: "xlsx",
      type: "array",
    });

    const blob = new Blob([excelBuffer], {
      type: "application/octet-stream",
    });

    saveAs(blob, `Margins_${Date.now()}.xlsx`);
  };

  // ✅ CSV DOWNLOAD
  const handleExportCSV = () => {
    const data = getExportData();

    const headers = (marginColumns as any[])
      .map((col: any) => col.dataIndex)
      .filter(Boolean);

    const worksheet = XLSX.utils.json_to_sheet(data || [], {
      header: headers,
      skipHeader: false,
    });

    const csv = XLSX.utils.sheet_to_csv(worksheet);

    const blob = new Blob([csv], {
      type: "text/csv;charset=utf-8;",
    });

    saveAs(blob, `Margins_${Date.now()}.csv`);
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
              onClick={handleExportExcel}
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
              onClick={handleExportCSV}
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
