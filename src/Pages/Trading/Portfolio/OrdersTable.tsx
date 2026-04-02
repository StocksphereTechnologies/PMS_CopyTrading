import React, { useState, useEffect } from "react";
import { Table, Select } from "antd";
import { Order } from "../../../Services/orderService";

const { Option } = Select;

const columns = [
  {
    key: "symbol",
    title: "Symbol",
    dataIndex: "symbol",
    sorter: (a: any, b: any) =>
      String(a.symbol).localeCompare(String(b.symbol)),
  },
  {
    key: "trdAcc",
    title: "Trd Acc",
    dataIndex: "trdAcc",
    sorter: (a: any, b: any) =>
      String(a.trdAcc).localeCompare(String(b.trdAcc)),
  },
  {
    key: "pseAcc",
    title: "Pse Acc",
    dataIndex: "pseAcc",
    sorter: (a: any, b: any) =>
      String(a.pseAcc).localeCompare(String(b.pseAcc)),
  },
  {
    key: "id",
    title: "ID",
    dataIndex: "id",
    sorter: (a: any, b: any) =>
      String(a.id).localeCompare(String(b.id)),
  },
  {
    key: "updateTime",
    title: "Update Time",
    dataIndex: "updateTime",
    sorter: (a: any, b: any) =>
      String(a.updateTime).localeCompare(String(b.updateTime)),
    render: (value: string) => {
      if (!value) return "";

      const date = new Date(value);

      return date.toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: true,
      });
    }
  },
  {
    key: "status",
    title: "Status",
    dataIndex: "status",
    sorter: (a: any, b: any) =>
      String(a.status).localeCompare(String(b.status)),
  },
  {
    key: "qty",
    title: "Qty",
    dataIndex: "qty",
    sorter: (a: any, b: any) => Number(a.qty) - Number(b.qty),
  },
  {
    key: "price",
    title: "Price",
    dataIndex: "price",
    sorter: (a: any, b: any) => Number(a.price) - Number(b.price),
  },
  {
    key: "variety",
    title: "Variety",
    dataIndex: "variety",
    sorter: (a: any, b: any) =>
      String(a.variety).localeCompare(String(b.variety)),
  },
  {
    key: "trade",
    title: "Trade",
    dataIndex: "trade",
    sorter: (a: any, b: any) =>
      String(a.trade).localeCompare(String(b.trade)),
  },
  {
    key: "order",
    title: "Order",
    dataIndex: "order",
    sorter: (a: any, b: any) =>
      String(a.order).localeCompare(String(b.order)),
  },
  {
    key: "product",
    title: "Product",
    dataIndex: "product",
    sorter: (a: any, b: any) =>
      String(a.product).localeCompare(String(b.product)),
  },
  {
    key: "exch",
    title: "Exch",
    dataIndex: "exch",
    sorter: (a: any, b: any) =>
      String(a.exch).localeCompare(String(b.exch)),
  },
  {
    key: "trigPrc",
    title: "Trig Prc",
    dataIndex: "trigPrc",
    sorter: (a: any, b: any) => Number(a.trigPrc) - Number(b.trigPrc),
  },
  {
    key: "fillQty",
    title: "Fill Qty",
    dataIndex: "fillQty",
    sorter: (a: any, b: any) => Number(a.fillQty) - Number(b.fillQty),
  },
  {
    key: "pendQty",
    title: "Pend Qty",
    dataIndex: "pendQty",
    sorter: (a: any, b: any) => Number(a.pendQty) - Number(b.pendQty),
  },
  {
    key: "pubId",
    title: "Pub Id",
    dataIndex: "pubId",
    sorter: (a: any, b: any) => String(a.pubId).localeCompare(String(b.pubId)),
  },
  {
    key: "avgPrc",
    title: "Avg Prc",
    dataIndex: "avgPrc",
    sorter: (a: any, b: any) => Number(a.avgPrc) - Number(b.avgPrc),
  },
  {
    key: "exchId",
    title: "Exch Id",
    dataIndex: "exchId",
    sorter: (a: any, b: any) => String(a.exchId).localeCompare(String(b.exchId)),
  },
  {
    key: "parentId",
    title: "Parent Id",
    dataIndex: "parentId",
    sorter: (a: any, b: any) => String(a.parentId).localeCompare(String(b.parentId)),
  },
  {
    key: "discQty",
    title: "Disc Qty",
    dataIndex: "discQty",
    sorter: (a: any, b: any) => Number(a.discQty) - Number(b.discQty),
  },
  {
    key: "amo",
    title: "AMO",
    dataIndex: "amo",
    sorter: (a: any, b: any) => String(a.amo).localeCompare(String(b.amo)),
  },
  {
    key: "validity",
    title: "Validity",
    dataIndex: "validity",
    sorter: (a: any, b: any) => String(a.validity).localeCompare(String(b.validity)),
  },
  {
    key: "rejectReason",
    title: "Reject Reason",
    dataIndex: "rejectReason",
    sorter: (a: any, b: any) => String(a.rejectReason).localeCompare(String(b.rejectReason)),
  },
  {
    key: "brStatus",
    title: "Br Status",
    dataIndex: "brStatus",
    sorter: (a: any, b: any) => String(a.brStatus).localeCompare(String(b.brStatus)),
  },
  {
    key: "brExch",
    title: "Br Exch",
    dataIndex: "brExch",
    sorter: (a: any, b: any) => String(a.brExch).localeCompare(String(b.brExch)),
  },
  {
    key: "brSymbol",
    title: "Br Symbol",
    dataIndex: "brSymbol",
    sorter: (a: any, b: any) => String(a.brSymbol).localeCompare(String(b.brSymbol)),
  },
  {
    key: "day",
    title: "Day",
    dataIndex: "day",
    sorter: (a: any, b: any) => String(a.day).localeCompare(String(b.day)),
  },
  {
    key: "client",
    title: "Client",
    dataIndex: "client",
    sorter: (a: any, b: any) => String(a.client).localeCompare(String(b.client)),
  },
  {
    key: "platform",
    title: "Platform",
    dataIndex: "platform",
    sorter: (a: any, b: any) => String(a.platform).localeCompare(String(b.platform)),
  },
  {
    key: "broker",
    title: "Broker",
    dataIndex: "broker",
    sorter: (a: any, b: any) => String(a.broker).localeCompare(String(b.broker)),
  },
  {
    key: "copyTrace",
    title: "Copy Trace",
    dataIndex: "copyTrace",
    sorter: (a: any, b: any) => String(a.copyTrace).localeCompare(String(b.copyTrace)),
  },

];

interface OrdersTableProps {
  orders: Order[];
  loading: boolean;
  selectedRowKeys: React.Key[];
  setSelectedRowKeys: (keys: React.Key[]) => void;
}

const OrdersTable: React.FC<OrdersTableProps> = ({
  orders,
  loading,
  selectedRowKeys,
  setSelectedRowKeys
}) => {
  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => {
      setSelectedRowKeys(keys);
    }
  };

  const [filters, setFilters] = useState<{ [key: string]: string }>({});
  const [filteredData, setFilteredData] = useState<Order[]>([]);

  // update table when backend data changes
  useEffect(() => {
    setFilteredData(orders);
  }, [orders]);

  const handleColumnFilter = (value: string, key: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);

    let data = orders;

    Object.keys(newFilters).forEach((k) => {
      if (newFilters[k]) {
        data = data.filter((row: any) =>
          String(row[k])
            .toLowerCase()
            .includes(newFilters[k].toLowerCase())
        );
      }
    });

    setFilteredData(data);
  };

  const filterRow = (
    <tr>
      {columns.map((col: any) => (
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
      rowKey="id"
      rowSelection={rowSelection}
      loading={loading}
      pagination={{ pageSize: 20 }}
      columns={columns}
      dataSource={filteredData}
      onRow={(record) => ({
        onClick: () => {
          const selected = [...selectedRowKeys];

          if (selected.includes(record.id)) {
            setSelectedRowKeys(selected.filter((key) => key !== record.id));
          } else {
            selected.push(record.id);
            setSelectedRowKeys(selected);
          }
        },
      })}
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
                  <td
                    colSpan={columns.length}
                    style={{
                      textAlign: "center",
                      fontWeight: "bold",
                    }}
                  >
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
export const orderColumns = columns;
export default OrdersTable;