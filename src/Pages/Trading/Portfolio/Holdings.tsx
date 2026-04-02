import React, { useState } from "react";
import { Input, Button, Tooltip, Row, Col, } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import HoldingsTable from "./HoldingsTable";
import Swal from "sweetalert2";
import * as XLSX from "xlsx-js-style";
import { saveAs } from "file-saver";
import { holdingsColumns } from "./HoldingsTable";

const greyBtn = { background: "#6e6e6e", color: "#fff" };
const greenBtn = { background: "#11c26d", color: "#fff" };
const orangeBtn = { background: "#ff8c5a", color: "#fff" };

const Holdings: React.FC = () => {
  const [searchText, setSearchText] = useState("");
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [filteredData, setFilteredData] = useState<any[]>([]);

  const handleReset = () => {
    setSearchText("");
    setSelectedRowKeys([]);
  };

  const handleSelect = () => {
    const keys = filteredData.map((item: any) => item.insttoken || item.symbol);
    setSelectedRowKeys(keys);
  };

  const handleDeselect = () => {
    setSelectedRowKeys([]);
  };

  // ✅ EXCEL DOWNLOAD
  const handleExportExcel = () => {
    const headers = (holdingsColumns as any[])
      .flatMap((col: any) => col.children ? col.children : [col])
      .map((col: any) => col.dataIndex)
      .filter(Boolean);

    const worksheet = XLSX.utils.json_to_sheet(filteredData || [], {
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
    XLSX.utils.book_append_sheet(workbook, worksheet, "Holdings");

    const excelBuffer = XLSX.write(workbook, {
      bookType: "xlsx",
      type: "array",
    });

    const blob = new Blob([excelBuffer], {
      type: "application/octet-stream",
    });

    saveAs(blob, `Holdings_${Date.now()}.xlsx`);
  };

  // ✅ CSV DOWNLOAD
  const handleExportCSV = () => {
    const headers = (holdingsColumns as any[])
      .flatMap((col: any) => col.children ? col.children : [col])
      .map((col: any) => col.dataIndex)
      .filter(Boolean);

    const worksheet = XLSX.utils.json_to_sheet(filteredData || [], {
      header: headers,
      skipHeader: false,
    });

    const csv = XLSX.utils.sheet_to_csv(worksheet);

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });

    saveAs(blob, `Holdings_${Date.now()}.csv`);
  };

  const placeOrder = async (type: "BUY" | "SELL") => {
    try {
      const selectedHoldings = filteredData.filter((item: any) =>
        selectedRowKeys.includes(item.insttoken || item.symbol)
      );

      if (selectedHoldings.length === 0) {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "Please select at least one holding",
        });
        return;
      }

      for (const h of selectedHoldings) {

        await fetch("/api/v1/trades", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({

            // ✅ REQUIRED FIELDS
            symbol: h.symbol,
            exchange: h.exchange,

            side: type,
            quantity: h.totqty,
            order_type: "MARKET",

            // 🔥 IMPORTANT (THIS WAS MISSING)
            account_ids: [h.account_id],

            // ✅ REQUIRED FOR BROKER
            product: "DELIVERY",
            variety: "regular",

            // Optional
            price: 0,
          }),
        });

      }
      await Swal.fire({
        icon: "success",
        title: "Success",
        text: `${type} order placed successfully`,
      });

    } catch (err) {
      console.error(err);

      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Order failed, Please try again",
      });
    }
  };

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={8} style={{ marginBottom: 8 }}>
        <Col>
          <Tooltip title="Reset Holdings Filter">
            <Button style={greyBtn} onClick={handleReset}>
              Reset
            </Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Select all holdings (If you have filtered the table, then only the filtered holdings will be selected.)">
            <Button style={greyBtn} onClick={handleSelect}>
              Select
            </Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Deselect all holdings">
            <Button style={greyBtn} onClick={handleDeselect}>
              Deselect
            </Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Square-Off (SELL) one or more holdings with a single click!">
            <Button style={orangeBtn} onClick={() => placeOrder("SELL")}>
              Square-Off
            </Button>
          </Tooltip>
        </Col>

        <Col>
          <Tooltip title="Increase (BUY) one or more holdings with a single click!">
            <Button style={greenBtn} onClick={() => placeOrder("BUY")}>
              Increase
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
          <Tooltip title="Download in Csv format">
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

      <HoldingsTable
        searchText={searchText}
        setFilteredData={setFilteredData}
        selectedRowKeys={selectedRowKeys}
        setSelectedRowKeys={setSelectedRowKeys}
      />
    </div>
  );
};

export default Holdings;
