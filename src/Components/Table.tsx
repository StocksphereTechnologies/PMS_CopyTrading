import React, { useEffect, useState } from "react";
import { Table, Input, Button, Space, Select } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import type { TableProps } from 'antd';
import * as XLSX from "xlsx-js-style";
import { saveAs } from "file-saver";

interface SmartTableProps extends Omit<TableProps<any>, 'title'> {
    title?: string;
    exportButtons?: boolean;
    searchable?: boolean;
}

const SmartTable: React.FC<SmartTableProps> = ({
    title,
    exportButtons = true,
    searchable = true,
    columns = [],
    dataSource = [],
    ...rest
}) => {

    const [filters, setFilters] = useState<any>({});
    const [filteredData, setFilteredData] = useState<any[]>([...(dataSource || [])]);
    const [searchText, setSearchText] = useState("");

    useEffect(() => {
        setFilteredData([...(dataSource || [])]);
    }, [dataSource]);
    useEffect(() => {

        let tempData = [...(dataSource || [])];

        // Global Search
        if (searchText) {
            tempData = tempData.filter((row: any) =>
                Object.values(row).some((value) =>
                    String(value ?? "")
                        .toLowerCase()
                        .includes(searchText.toLowerCase())
                )
            );
        }

        // Column Filters
        Object.keys(filters).forEach((k) => {
            if (filters[k] !== undefined && filters[k] !== "") {
                tempData = tempData.filter((row: any) =>
                    String(row[k] ?? "")
                        .toLowerCase()
                        .includes(filters[k].toLowerCase())
                );
            }
        });

        setFilteredData(tempData);

    }, [dataSource, filters, searchText]);
    const handleColumnFilter = (value: string, key: string) => {

        const newFilters = { ...filters, [key]: value }
        setFilters(newFilters)

        let tempData = [...(dataSource || [])]
        Object.keys(newFilters).forEach((k) => {
            if (newFilters[k]) {
                tempData = tempData.filter((row: any) =>
                    String(row[k] ?? "")
                        .toLowerCase()
                        .includes(newFilters[k].toLowerCase())
                )
            }
        })

        setFilteredData(tempData)
    }

    // ✅ EXCEL DOWNLOAD
    const handleExportExcel = () => {
        const headers = (columns as any[])
            .flatMap((col: any) => col.children ? col.children : [col])
            .map((col: any) => col.dataIndex)
            .filter(Boolean);

        const worksheet = XLSX.utils.json_to_sheet(filteredData || [], {
            header: headers,
            skipHeader: false,
        });

        // ✅ MAKE HEADER BOLD
        headers.forEach((header: string, index: number) => {
            const cellAddress = XLSX.utils.encode_cell({ r: 0, c: index });

            if (worksheet[cellAddress]) {
                worksheet[cellAddress].s = {
                    font: {
                        bold: true,
                    },
                };
            }
        });

        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, title || "Summary");

        const excelBuffer = XLSX.write(workbook, {
            bookType: "xlsx",
            type: "array",
        });

        const blob = new Blob([excelBuffer], {
            type: "application/octet-stream",
        });

        saveAs(blob, `${title || "Summary"}_${Date.now()}.xlsx`);
    };

    // ✅ CSV DOWNLOAD
    const handleExportCSV = () => {
        const headers = (columns as any[])
            .flatMap((col: any) => col.children ? col.children : [col])
            .map((col: any) => col.dataIndex)
            .filter(Boolean);

        const worksheet = XLSX.utils.json_to_sheet(filteredData || [], {
            header: headers,
            skipHeader: false,
        });

        const csv = XLSX.utils.sheet_to_csv(worksheet);

        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });

        saveAs(blob, `${title || "Summary"}_${Date.now()}.csv`);
    };

    const leafColumns = (columns as any[]).flatMap((col: any) =>
        col.children ? col.children : [col]
    )

    const filterRow = (
        <tr>
            {leafColumns.map((col: any) => (
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
    )

    return (
        <div style={{ background: '#fff', borderRadius: 8, padding: 16, marginBottom: 24 }}>

            {title && (
                <h3 style={{ color: '#00b39f', marginBottom: 16 }}>{title}</h3>
            )}

            <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }} wrap>

                {searchable && (
                    <Input
                        placeholder="Search..."
                        prefix={<SearchOutlined />}
                        style={{ width: 250 }}
                        allowClear
                        value={searchText}
                        onChange={(e) => setSearchText(e.target.value)}
                    />
                )}

            </Space>

            <Space style={{ marginBottom: 16 }}>
                {exportButtons && <>
                    <Button
                        style={{ background: "#36454F", color: "#fff", fontWeight: "bold" }}
                        onClick={handleExportExcel}
                    >
                        Excel
                    </Button>

                    <Button
                        style={{ background: "#36454F", color: "#fff", fontWeight: "bold" }}
                        onClick={handleExportCSV}
                    >
                        CSV
                    </Button>
                </>}
            </Space>

            <Table
                rowKey="tradingAcc"
                bordered
                columns={columns}
                dataSource={filteredData}
                scroll={{ x: "max-content" }}
                pagination={false}
                components={{
                    header: {
                        wrapper: (props: any) => (
                            <thead {...props}>
                                {props.children}
                                {filterRow}
                            </thead>
                        ),
                    },
                }}
                {...rest}
            />

        </div>
    );
};

export default SmartTable;