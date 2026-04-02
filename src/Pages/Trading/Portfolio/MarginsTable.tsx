import React, { useMemo } from "react";
import { Table } from "antd";
import { AccountMargin } from "../../../Services/marginService";

type SegmentFilter = "all" | "equity" | "commodity";

interface MarginsTableProps {
  margins: AccountMargin[];
  loading: boolean;
  searchText: string;
  segmentFilter: SegmentFilter;
}

interface TableRow {
  key: string;
  pseAcc: string;
  trdAcc: string;
  category: string;
  total: string;
  net: string;
  funds: string;
  utilized: string;
  available: string;
  collateral: string;
  realmtm: string;
  unrealmtm: string;
  adhoc: string;
  span: string;
  exposure: string;
  payin: string;
  payout: string;
  day: string;
  broker: string;
}

const formatCurrency = (value: number): string => {
  return `₹${value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

const parseCurrency = (val: any) =>
  parseFloat(String(val).replace(/[^0-9.-]+/g, "")) || 0;

const columns = [
  {
    key: "pseAcc",
    title: "Pse Acc",
    dataIndex: "pseAcc",
    sorter: (a: any, b: any) => String(a.pseAcc).localeCompare(String(b.pseAcc)),
  },
  {
    key: "trdAcc",
    title: "Trd Acc",
    dataIndex: "trdAcc",
    sorter: (a: any, b: any) => String(a.trdAcc).localeCompare(String(b.trdAcc)),
  },
  {
    key: "category",
    title: "Category",
    dataIndex: "category",
    sorter: (a: any, b: any) => String(a.category).localeCompare(String(b.category)),
  },
  {
    key: "total",
    title: "Total",
    dataIndex: "total",
    sorter: (a: any, b: any) => parseCurrency(a.total) - parseCurrency(b.total),
  },
  {
    key: "net",
    title: "Net",
    dataIndex: "net",
    sorter: (a: any, b: any) => parseCurrency(a.net) - parseCurrency(b.net),
  },
  {
    key: "funds",
    title: "Funds",
    dataIndex: "funds",
    sorter: (a: any, b: any) => parseCurrency(a.funds) - parseCurrency(b.funds),
  },
  {
    key: "utilized",
    title: "Utilized",
    dataIndex: "utilized",
    sorter: (a: any, b: any) => parseCurrency(a.utilized) - parseCurrency(b.utilized),
  },
  {
    key: "available",
    title: "Available",
    dataIndex: "available",
    sorter: (a: any, b: any) => parseCurrency(a.available) - parseCurrency(b.available),
  },
  {
    key: "collateral",
    title: "Collateral",
    dataIndex: "collateral",
    sorter: (a: any, b: any) => parseCurrency(a.collateral) - parseCurrency(b.collateral),
  },
  {
    key: "realmtm",
    title: "Real MTM",
    dataIndex: "realmtm",
    sorter: (a: any, b: any) => parseCurrency(a.realmtm) - parseCurrency(b.realmtm),
  },
  {
    key: "unrealmtm",
    title: "Unreal MTM",
    dataIndex: "unrealmtm",
    sorter: (a: any, b: any) => parseCurrency(a.unrealmtm) - parseCurrency(b.unrealmtm),
  },
  {
    key: "adhoc",
    title: "Adhoc",
    dataIndex: "adhoc",
    sorter: (a: any, b: any) => parseCurrency(a.adhoc) - parseCurrency(b.adhoc),
  },
  {
    key: "span",
    title: "Span",
    dataIndex: "span",
    sorter: (a: any, b: any) => parseCurrency(a.span) - parseCurrency(b.span),
  },
  {
    key: "exposure",
    title: "Exposure",
    dataIndex: "exposure",
    sorter: (a: any, b: any) => parseCurrency(a.exposure) - parseCurrency(b.exposure),
  },
  {
    key: "payin",
    title: "Payin",
    dataIndex: "payin",
    sorter: (a: any, b: any) => parseCurrency(a.payin) - parseCurrency(b.payin),
  },
  {
    key: "payout",
    title: "Payout",
    dataIndex: "payout",
    sorter: (a: any, b: any) => parseCurrency(a.payout) - parseCurrency(b.payout),
  },
  {
    key: "day",
    title: "Day",
    dataIndex: "day",
    sorter: (a: any, b: any) => String(a.day).localeCompare(String(b.day)),
  },
  {
    key: "broker",
    title: "Broker",
    dataIndex: "broker",
    sorter: (a: any, b: any) => String(a.broker).localeCompare(String(b.broker)),
  },
];

const MarginsTable: React.FC<MarginsTableProps> = ({
  margins,
  loading,
  searchText,
  segmentFilter,
}) => {
  const tableData = useMemo(() => {
    const rows: TableRow[] = [];

    margins.forEach((margin) => {
      // Filter by search text
      const matchesSearch =
        !searchText ||
        margin.trading_login_id.toLowerCase().includes(searchText.toLowerCase()) ||
        margin.broker_name.toLowerCase().includes(searchText.toLowerCase()) ||
        (margin.nickname && margin.nickname.toLowerCase().includes(searchText.toLowerCase()));

      if (!matchesSearch) return;

      // Add equity row
      if ((segmentFilter === "all" || segmentFilter === "equity") && margin.equity) {
        const equity = margin.equity;
        rows.push({
          key: `${margin.account_id}-equity`,
          pseAcc: margin.nickname || "",
          trdAcc: margin.trading_login_id,
          category: "EQUITY",
          total: formatCurrency(equity.available.opening_balance),
          net: formatCurrency(equity.net),
          funds: formatCurrency(equity.available.cash),
          utilized: formatCurrency(
            equity.utilised.debits + equity.utilised.span + equity.utilised.exposure
          ),
          available: formatCurrency(equity.available.live_balance),
          collateral: formatCurrency(equity.available.collateral),
          realmtm: formatCurrency(equity.utilised.m2m_realised),
          unrealmtm: formatCurrency(equity.utilised.m2m_unrealised),
          adhoc: formatCurrency(equity.available.adhoc_margin),
          span: formatCurrency(equity.utilised.span),
          exposure: formatCurrency(equity.utilised.exposure),
          payin: formatCurrency(equity.available.intraday_payin),
          payout: formatCurrency(equity.utilised.payout),
          day: new Date(margin.last_updated).toLocaleDateString(),
          broker: margin.broker_name,
        });
      }

      // Add commodity row if exists
      if (
        (segmentFilter === "all" || segmentFilter === "commodity") &&
        margin.commodity
      ) {
        const commodity = margin.commodity;
        rows.push({
          key: `${margin.account_id}-commodity`,
          pseAcc: margin.nickname || "",
          trdAcc: margin.trading_login_id,
          category: "COMMODITY",
          total: formatCurrency(commodity.available.opening_balance),
          net: formatCurrency(commodity.net),
          funds: formatCurrency(commodity.available.cash),
          utilized: formatCurrency(
            commodity.utilised.debits + commodity.utilised.span + commodity.utilised.exposure
          ),
          available: formatCurrency(commodity.available.live_balance),
          collateral: formatCurrency(commodity.available.collateral),
          realmtm: formatCurrency(commodity.utilised.m2m_realised),
          unrealmtm: formatCurrency(commodity.utilised.m2m_unrealised),
          adhoc: formatCurrency(commodity.available.adhoc_margin),
          span: formatCurrency(commodity.utilised.span),
          exposure: formatCurrency(commodity.utilised.exposure),
          payin: formatCurrency(commodity.available.intraday_payin),
          payout: formatCurrency(commodity.utilised.payout),
          day: new Date(margin.last_updated).toLocaleDateString(),
          broker: margin.broker_name,
        });
      }
    });

    return rows;
  }, [margins, searchText, segmentFilter]);

  return (
    <Table
      bordered
      loading={loading}
      pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `Total ${total} rows` }}
      columns={columns}
      dataSource={tableData}
      scroll={{ x: "max-content" }}
      locale={{ emptyText: "No margin data available. Please add and validate trading accounts." }}
    />
  );
};
export const marginColumns = columns;
export default MarginsTable;
