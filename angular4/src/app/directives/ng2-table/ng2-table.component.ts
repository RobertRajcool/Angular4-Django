import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-ng2-table',
  templateUrl: './ng2-table.component.html',
  styleUrls: ['./ng2-table.component.scss']
})
export class Ng2TableComponent implements OnInit {

    @Input() screenName: string;
    @Input('rows') rows: Array<any>;
    @Input('columns') columns: Array<any>;
    @Output() event = new EventEmitter();

    page: number = 1;
    itemsPerPage: number = 10;
    maxSize: number = 5;
    numPages: number = 1;

    _config: any = {
        className: 'table-striped table-bordered',
        paging: true,
        sorting: { columns: this.columns },
        commonFilter: false,
        filtering: { filterString: '', columnName: 'user_name' }
    };
   
    constructor() { }

    ngOnInit() {
        let action_obj = { title: 'Actions', links: ['View','Edit', 'Delete'] };
        this.columns.push(action_obj);
        this.onChangeTable(this._config);
    }

    @Input()
    set config(config: any) {
        if (config) {
        this._config = config;
        }
    }

    get config() {
        return this._config;
    }

    linkClicked(data: any): any {
        this.event.emit({
                data: data
            });
    }

    changePage(page: any, data: Array<any> = this._config.ng2TableData): Array<any> {
        let start = (page.page - 1) * page.itemsPerPage;
        let end = page.itemsPerPage > -1 ? (start + page.itemsPerPage) : data.length;
        return data.slice(start, end);
    }

    changeSort(data: any, config: any): any {
        if (!config.sorting) {
            return data;
        }

        let columns = this._config.sorting.columns || [];
        let columnName: string = void 0;
        let sort: string = void 0;

        for (let i = 0; i < columns.length; i++) {
            if (columns[i].sort !== '' && columns[i].sort !== false) {
                columnName = columns[i].name;
                sort = columns[i].sort;
            }
        }

        if (!columnName) {
            return data;
        }

        // simple sorting
        return data.sort((previous: any, current: any) => {
            if (previous[columnName] > current[columnName]) {
                return sort === 'desc' ? -1 : 1;
            } else if (previous[columnName] < current[columnName]) {
                return sort === 'asc' ? -1 : 1;
            }
            return 0;
        });
    }

    changeFilter(data: any, config: any): any {
        let filteredData: Array<any> = data;
        this.columns.forEach((column: any) => {
            if (column.filtering) {
                filteredData = filteredData.filter((item: any) => {
                    return item[column.name].match(new RegExp(column.filtering.filterString, "i"));
                });
            }
        });

        if (!config.filtering) {
            return filteredData;
        }

        if (config.filtering.columnName) {
            return filteredData.filter((item: any) =>
                item[config.filtering.columnName].match(this.config.filtering.filterString));                
        }
        
        let tempArray: Array<any> = [];
        filteredData.forEach((item: any) => {
            let flag = false;
            this.columns.forEach((column: any) => {
                if (item[column.name].toString().match(this._config.filtering.filterString)) {
                    flag = true;
                }
            });
            if (flag) {
                tempArray.push(item);
            }
        });
        filteredData = tempArray;

        return filteredData;
    }

    onChangeTable(config: any, page: any = { page: this.page, itemsPerPage: this.itemsPerPage }): any {
        if (config.filtering) {
            Object.assign(this._config.filtering, config.filtering);
        }
        if (config.sorting) {
            Object.assign(this._config.sorting, config.sorting);
        }
        let tableData = this._config.ng2TableData ? this._config.ng2TableData : this.rows;
        let filteredData = this.changeFilter(tableData, this._config);
        let sortedData = this.changeSort(filteredData, this._config);
        this.rows = page && config.paging ? this.changePage(page, sortedData) : sortedData;
        this._config.length = sortedData.length;
    }
}
