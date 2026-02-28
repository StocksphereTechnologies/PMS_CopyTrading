import React, { useEffect, useState } from "react";
import { Table, Select } from "antd";
import { positionService, Position } from "../../../Services/positionService";

const { Option } = Select;

const initialData: any[] = [];

const parseCurrency = (val: any) =>
  parseFloat(String(val).replace(/[^0-9.-]+/g, "")) || 0;

const columns = [
    {
      key: "m2m",
      title: "M2M",
      dataIndex: "m2m",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.m2m) - parseCurrency(b.m2m),
    },
    {
      key: "pnl",
      title: "PnL",
      dataIndex: "pnl",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.pnl) - parseCurrency(b.pnl),
    },
    {
      key: "atpnl",
      title: "AT PnL",
      dataIndex: "atpnl",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.atpnl) - parseCurrency(b.atpnl),
    },
    {
      key: "symbol",
      title: "Symbol",
      dataIndex: "symbol",
      width: 100,
      sorter: (a: any, b: any) => String(a.symbol).localeCompare(String(b.symbol)),
    },
    {
      key: "realpl",
      title: "Real PL",
      dataIndex: "realpl",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.realpl) - parseCurrency(b.realpl),
    },
    {
      key: "unrealpl",
      title: "Unreal PL",
      dataIndex: "unrealpl",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.unrealpl) - parseCurrency(b.unrealpl),
    },
    {
      key: "netqty",
      title: "Net Qty",
      dataIndex: "netqty",
      width: 100,
      sorter: (a: any, b: any) => Number(a.netqty) - Number(b.netqty),
    },
    {
      key: "ltp",
      title: "Ltp",
      dataIndex: "ltp",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.ltp) - parseCurrency(b.ltp),
    },
    {
      key: "pseacc",
      title: "Pse Acc",
      dataIndex: "pseacc",
      width: 100,
      sorter: (a: any, b: any) => String(a.pseacc).localeCompare(String(b.pseacc)),
    },
    {
      key: "trdacc",
      title: "Trd Acc",
      dataIndex: "trdacc",
      width: 100,
      sorter: (a: any, b: any) => String(a.trdacc).localeCompare(String(b.trdacc)),
    },
    {
      key: "buyqty",
      title: "Buy Qty",
      dataIndex: "buyqty",
      width: 100,
      sorter: (a: any, b: any) => Number(a.buyqty) - Number(b.buyqty),
    },
    {
      key: "sellqty",
      title: "Sell Qty",
      dataIndex: "sellqty",
      width: 100,
      sorter: (a: any, b: any) => Number(a.sellqty) - Number(b.sellqty),
    },
    {
      key: "buyval",
      title: "Buy Val",
      dataIndex: "buyval",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.buyval) - parseCurrency(b.buyval),
    },
    {
      key: "sellval",
      title: "Sell Val",
      dataIndex: "sellval",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.sellval) - parseCurrency(b.sellval),
    },
    {
      key: "netval",
      title: "Net Val",
      dataIndex: "netval",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.netval) - parseCurrency(b.netval),
    },
    {
      key: "bavg",
      title: "B Avg Prc",
      dataIndex: "bavg",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.bavg) - parseCurrency(b.bavg),
    },
    {
      key: "savg",
      title: "S Avg Prc",
      dataIndex: "savg",
      width: 100,
      sorter: (a: any, b: any) => parseCurrency(a.savg) - parseCurrency(b.savg),
    },
    {
      key: "state",
      title: "State",
      dataIndex: "state",
      width: 100,
      sorter: (a: any, b: any) => String(a.state).localeCompare(String(b.state)),
    },
    {
      key: "direction",
      title: "Direction",
      dataIndex: "direction",
      width: 100,
      sorter: (a: any, b: any) => String(a.direction).localeCompare(String(b.direction)),
    },
    {
      key: "type",
      title: "Type",
      dataIndex: "type",
      width: 100,
      sorter: (a: any, b: any) => String(a.type).localeCompare(String(b.type)),
    },
    {
      key: "category",
      title: "Category",
      dataIndex: "category",
      width: 100,
      sorter: (a: any, b: any) => String(a.category).localeCompare(String(b.category)),
    },
    {
      key: "broker",
      title: "Broker",
      dataIndex: "broker",
      width: 100,
      sorter: (a: any, b: any) => String(a.broker).localeCompare(String(b.broker)),
    },
    {
      key: "overqty",
      title: "Overnight Qty",
      dataIndex: "overqty",
      width: 100,
      sorter: (a: any, b: any) => String(a.overqty).localeCompare(String(b.overqty)),
    },
    {
      key: "multiplier",
      title: "Multiplier",
      dataIndex: "multiplier",
      width: 100,
      sorter: (a: any, b: any) => String(a.multiplier).localeCompare(String(b.multiplier)),
    },
    {
      key: "exch",
      title: "Exch",
      dataIndex: "exch",
      width: 100,
      sorter: (a: any, b: any) => String(a.exch).localeCompare(String(b.exch)),
    },
    {
      key: "brexch",
      title: "Br Exch",
      dataIndex: "brexch",
      width: 100,
      sorter: (a: any, b: any) => String(a.brexch).localeCompare(String(b.brexch)),
    },
    {
      key: "brsymbol",
      title: "BR Symbol",
      dataIndex: "brsymbol",
      width: 120,
      sorter: (a: any, b: any) => String(a.brsymbol).localeCompare(String(b.brsymbol)),
    },
    {
      key: "day",
      title: "Day",
      dataIndex: "day",
      width: 100,
      sorter: (a: any, b: any) => String(a.day).localeCompare(String(b.day)),
    },
    {
      key: "platform",
      title: "Platform",
      dataIndex: "platform",
      width: 100,
      sorter: (a: any, b: any) => String(a.platform).localeCompare(String(b.platform)),
    },
    {
      key: "accid",
      title: "Acc ID",
      dataIndex: "accid",
      width: 120,
      sorter: (a: any, b: any) => String(a.accid).localeCompare(String(b.accid)),
    },
    {
      key: "id",
      title: "ID",
      dataIndex: "id",
      width: 120,
      sorter: (a: any, b: any) => String(a.id).localeCompare(String(b.id)),
    },

  ];

  


interface PositionTableProps {
  setPositions: (positions: Position[]) => void;
  searchText: string;
  openOnly: boolean;
}

const PositionTable: React.FC<PositionTableProps> = ({ setPositions, searchText, openOnly }) => {
  const [data, setData] = useState<Position[]>([]);
  const [filters, setFilters] = useState<{ [key: string]: string }>({});
  const [filteredData, setFilteredData] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPositions();
  }, [openOnly]); // Re-fetch when filter changes

  const fetchPositions = async () => {
    try {
      setLoading(true);
      const response = await positionService.getAll(openOnly);
      const positions = response.positions;
      setData(positions);
      setFilteredData(positions);
      setPositions(positions);
    } catch (err) {
      console.error("Failed to fetch positions", err);
    } finally {
      setLoading(false);
    }
  };

  const handleColumnFilter = (value: string, key: string) => {
  const newFilters = { ...filters, [key]: value };
  setFilters(newFilters);

  let tempData = data;

  Object.keys(newFilters).forEach((k) => {
    if (newFilters[k]) {
      tempData = tempData.filter((row: any) =>
        String(row[k] ?? "")
          .toLowerCase()
          .includes(newFilters[k].toLowerCase())
      );
    }
  });

  setFilteredData(tempData);
};

useEffect(() => {
  let tempData = data;

  if (searchText) {
    tempData = tempData.filter((row: any) =>
      Object.values(row).some((val) =>
        String(val).toLowerCase().includes(searchText.toLowerCase())
      )
    );
  }

  setFilteredData(tempData);
}, [searchText, data]);

  const filterRow = (
    <tr>
      {columns.map((col) => (
        <th key={col.dataIndex}>
          <Select
            allowClear
            size="small"
            style={{ width: "100%" }}
            value={filters[col.dataIndex]}
            onChange={(v) => handleColumnFilter(v || "", col.dataIndex)}
          />
        </th>
      ))}
    </tr>
  );

  return (
    <Table
      bordered
      loading={loading}
      pagination={false}
      columns={columns}
      dataSource={filteredData}
      rowKey="id"
      scroll={{ x: "max-content" }}
      locale={{ emptyText: "" }}
      components={{
        header: {
          wrapper: (props: any) => (
            <thead {...props}>
              {props.children}
              {filterRow}
            </thead>
          ),
        },
        body: {
          wrapper: (props: any) =>
            filteredData.length === 0 ? (
              <tbody>
                <tr>
                  <td colSpan={columns.length} style={{ textAlign: "center" }}>
                    No Data Available in table
                  </td>
                </tr>
              </tbody>
            ) : (
              <tbody {...props} />
            ),
        },
      }}
    />
  );
};

export default PositionTable;