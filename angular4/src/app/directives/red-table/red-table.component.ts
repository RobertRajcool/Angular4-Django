import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { AuthHttp } from "angular2-jwt";
import { Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { baseURL } from 'app/parameters';
import { Router, ActivatedRoute, NavigationStart, NavigationEnd } from "@angular/router";
import { DatePipe, LocationStrategy } from '@angular/common';

@Component({
    selector: 'app-red-table',
    templateUrl: './red-table.component.html',
    styleUrls: ['./red-table.component.scss'],
    providers: [DatePipe]
})
export class RedTableComponent implements OnInit {
    screenName: string;
    classToAdd: string;
    fetchUrl: string;
    @Input() backend_pdfreport_fetchUrl: string
    @Input() backend_excereport_fetchUrl: string
    @Input() backend_pdfreport_Filters: string
    @Input() backend_excereport_Filters: string
    @Input() addButtonInfo: any;
    @Input() commonFilter: any;
    @Input() limit: number;
    @Input('columns') columns: Array<any>;
    @Output() event = new EventEmitter();
    @Output() refreshedData: EventEmitter<any> = new EventEmitter();
    @Input() limitOptions: Array<number> = [5, 10, 15, 20, 25];
    @Output() filtersApplied: EventEmitter<any> = new EventEmitter();
    @Output() previousAppliedFilters: EventEmitter<any> = new EventEmitter();

    public page: number = 1;
    public endVal: number = 5;
    public startVal: number = 0;
    public rows: Array<Object> = [];
    public itemsPerPage: number = 5;
    public maxSize: number = 5;
    public length: number = 0;
    public totalRecords: number = 0;
    public constFilters: Object = {};
    public columnFilter: Array<Object> = [];
    public isSearchEnabled: boolean = false;
    public dataLoaded: boolean = false;
    public dataLoading: boolean = false;
    public displayCommonFilter: boolean = false;
    public imageColumns: Array<string> = [];
    public colourButtonColumns: Array<string> = [];
    public dateColumns: Array<Object> = [];
    public sortColumnName: string = '';
    public searchText: string = '';
    public selectedRecords: Array<any> = [];
    public config: any = {
        paging: true,
        itemsPerPage: 5,
        sorting: true,
        filtering: { filterString: '' },
        className: ['table-striped', 'table-hover', 'actions-list', 'filter-list-fields']
    };
    public exchange_rate: number = 0;
    public currentState: string = '';
    public filterValues: Array<Object> = [];
    public url: any;
    public canAdd: boolean;
    subscriptions: Object = {};
    value: any;


    private classNamesList: Object = {
        "View": { name: "View", iconClass: "fa fa-eye", mainClass: "btn-info" },
        "View Details": { name: "View Details", iconClass: "fa fa-eye", mainClass: "btn-info" },
        "Edit": { name: "Edit", iconClass: "fa fa-edit", mainClass: "btn-warning" },
        "Delete": { name: "Delete", iconClass: "fa fa-remove", mainClass: "btn-danger" },
        "Manage products": { name: "Manage products", iconClass: "fa fa-product-hunt", mainClass: "btn-primary" },
        "Create": { name: "Create", iconClass: "fa fa-plus", mainClass: "btn-primary" },
        "Refresh": { name: "Refresh", iconClass: "fa fa-refresh", mainClass: "btn-primary" },
        "Start": { name: "Start", iconClass: "fa fa-play", mainClass: "btn-success" },
        "Stop": { name: "Stop", iconClass: "fa fa-stop", mainClass: "btn-danger" },
        "Add": { name: "Add", iconClass: "fa fa-plus", mainClass: "btn-primary" },
        "Generate SO": { name: "Generate SO", iconClass: "fa fa-file-text", mainClass: "btn-primary" },
        "Send": { name: "Send", iconClass: "", mainClass: "btn-primary" },
        "Approve Orders": { name: "Approve Orders", iconClass: "fa fa-check", mainClass: "btn-success" },
        "Approve": { name: "Approve", iconClass: "fa fa-check", mainClass: "btn-success" },
        "Reject": { name: "Reject", iconClass: "fa fa-ban", mainClass: "btn-warning" },
        "Add To Cart": { name: "Add To Cart", iconClass: "fa fa-cart-plus", mainClass: "btn-primary" },
        "View PDF": { name: "View PDF", iconClass: "fa fa-eye", mainClass: "btn-info" },
        "Pay": { name: "Pay", iconClass: "fa fa-credit-card-alt", mainClass: "btn-primary" },
        "New Tab": { name: "New Tab", iconClass: "fa fa-external-link-square", mainClass: "btn-info" },
        "Cancel Subscription": { name: "Cancel Request", iconClass: "fa fa-remove", mainClass: "btn-danger" },
        "Suspend Subscription": { name: "Suspend Subscription", iconClass: "fa fa-remove", mainClass: "btn-danger" },
        "Renewal Subscription": { name: "Renewal Subscription", iconClass: "fa fa-retweet", mainClass: "btn-primary" },
        "Downgrade Request": { name: "Downgrade Request", iconClass: "fa fa-minus", mainClass: "btn-danger" },
        "Change Billing Cycle": { name: "Change Billing Cycle", iconClass: "fa fa-clock-o", mainClass: "btn-primary" },
        "Enable": { name: "Enable", iconClass: "fa fa-toggle-on", mainClass: "btn-primary" },
        "Disable": { name: "Disable", iconClass: "fa fa-toggle-off", mainClass: "btn-primary" },
        "Change Status": { name: 'Change Status', iconClass: "fa fa-clock-o", mainClass: "btn-primary" },
        "Delink": { name: "Delink", iconClass: "fa fa-ban", mainClass: "btn-warning" },
    }

    private data: Array<any> = (this.rows) ? this.rows : [];

    public constructor(private http: AuthHttp, private router: Router, private datePipe: DatePipe, private route: ActivatedRoute, private location: LocationStrategy) {
    }

    public ngOnInit(): void {
        this.currentState = this.router.url;
        this.itemsPerPage = this.limit;
        if (this.currentState) {
            let data = localStorage.getItem('filters') ? JSON.parse(localStorage.getItem('filters')) : {};
            if (data && this.currentState != data.url) {
                localStorage.removeItem('filters');
            }
        }
        if (this.classToAdd && this.classToAdd != '') {
            this.config.className.push(this.classToAdd);
        } else {
            if (this.screenName) {
                let name = this.screenName;
                let className = name.replace(/\s/g, '_').replace(/\./g, '_').toLocaleLowerCase();
                this.config.className.push(className);
            }
        }

        if (this.commonFilter && this.commonFilter.columnName) {
            this.displayCommonFilter = true;
            this.config.filtering = this.commonFilter;
        }
        this.setColumnDetails();
        this.config.sorting = { columns: this.columns };
        this.config.itemsPerPage = this.itemsPerPage;

        /* Filter logic*/
        let localStorageData = localStorage.getItem('filters') ? JSON.parse(localStorage.getItem('filters')) : {};
        if(localStorageData) {
            if (this.currentState == localStorageData.url) {
                this.limit = localStorageData.limit ? localStorageData.limit : this.itemsPerPage;
                this.itemsPerPage = this.limit;
                this.endVal = localStorageData.end ? localStorageData.end : this.itemsPerPage;
                if (this.endVal > this.itemsPerPage) {
                    this.page = localStorageData.page ? localStorageData.page : this.page;
                    this.startVal = localStorageData.start ? localStorageData.start : 0;
                } else {
                    this.startVal = 0;
                }
                if (localStorageData.filter_value && localStorageData.filter_value != 'undefined') {
                    this.filterValues = this.filterValues.length > 0 ? this.filterValues : localStorageData.filter_value;
                } else {
                    this.filterValues = this.filterValues.length > 0 ? this.filterValues : [];
                }
                if (this.filterValues.length > 0) {
                    this.filterValues.forEach((column: any) => {
                        if (column.name == 'searchText') {
                            this.searchText = column.value;
                        } else if (column.name == 'order_by') {
                            this.sortColumnName = column.value
                        } else {
                            if (column.name != 'page' && column.name != 'start' && column.name != 'end' && column.name != 'limit') {
                                this.constFilters[column.name] = column.value;
                            }
                        }
                    });
                    this.previousAppliedFilters.emit(this.constFilters);
                }
            } else {
                this.startVal = 0;
                this.endVal = this.itemsPerPage;
            }
            this.columns.forEach((column: any) => {
                if (column.filtering) {
                    this.filterValues.forEach((filter: any) => {
                        if (column.name == filter.name) {
                            column.filtering.filterString = filter.value;
                        }
                    });
                }
            });
            this.fetchRecords(this.startVal, this.endVal);
        }
    }

    refreshPage() {
        let page = this.page;
        this.startVal = (page - 1) * this.itemsPerPage;
        this.endVal = this.startVal + this.itemsPerPage;
        this.fetchRecords(this.startVal, this.endVal);
    }

    // Update fetchUrl on changes
    @Input('fetchUrl')
    set changeFetchUrl(url: string) {
        if (url) this.fetchUrl = url;
        this.fetchRecords(0, this.limit);
    }

    // Update screen name on changes
    @Input('screenName')
    set changeScreenName(name: string) {
        this.screenName = name;
    }

    // Update screen name on changes
    @Input('classToAdd')
    set changeClassToAdd(name: string) {
        this.classToAdd = name;
    }

    // Assigning constant query filters
    @Input('queryParams')
    set constFilterData(filters: Object) {
        if (filters) this.constFilters = filters;
        else this.constFilters = {};
        this.page = 1;
        this.refreshPage();
    }

    // Updating configs
    @Input('config')
    set updateConfig(additionalConfigs: Object) {
        if (additionalConfigs) {
            Object.assign(this.config, additionalConfigs);
        }
    }

    setColumnDetails(): void {
        this.colourButtonColumns = [];
        this.imageColumns = [];
        this.dateColumns = [];
        this.columns.forEach((column: any) => {
            if (column.isColourButton) {
                this.colourButtonColumns.push(column.name);
            }
            if (column.isImage) {
                this.imageColumns.push(column.name);
            }
            if (column.dateFormat) {
                this.dateColumns.push({ name: column.name, format: column.dateFormat });
            }
            let field = column.name;
            if (field) {
                column.className = field.replace(/\./g, '_') + '_header';
            } else {
                column.className = 'actions_header';
                let links = column.links;
                if (links.length) {
                    let linkToReplace = []
                    links.forEach((link: any) => {
                        if (typeof link == 'string') {
                            if (this.classNamesList.hasOwnProperty(link)) {
                                linkToReplace.push(this.classNamesList[link])
                            } else {
                                linkToReplace.push({ name: link, iconClass: "", mainClass: "" })
                            }
                        } else {
                            linkToReplace.push(link);
                        }
                    });
                    column.links = linkToReplace;
                }
            }
        });
    }

    currentRequest: any = false;
    fetchRecords(offset: number, end: number): void {
        if (offset == 0 && this.page > 1) {
            this.page = 1;
        }
        if (this.fetchUrl == '') {
            //Todo: this is for developers
            alert('Please specify the fetchUrl value');
        }

        // To cancel the previous request
        if (this.currentRequest) {
            this.currentRequest.unsubscribe();
        }

        this.url = this.constructURL(offset, end);

        this.dataLoading = true;
        this.currentRequest = this.http
            .get(this.url)
            .map(Response => {
                let data = Response.json()
                if (data.hasOwnProperty('exchangeRate')) {
                    this.exchange_rate = data.exchangeRate
                }
                this.setPaginationDetails(data);
            })
            .catch(this.handleError).subscribe();
    }

    constructURL(offset: number, end: number): string {
        let queryParams: Object = {
            'offset': offset,
            'end': end
        };

        // Adding constant query params
        Object.assign(queryParams, this.constFilters);

        if (this.columnFilter.length) {
            this.columnFilter.forEach((column: any) => {
                queryParams[column.name] = column.value;
            });
        }
        if (this.sortColumnName != '') {
            queryParams['order_by'] = this.sortColumnName;
        }
        if (this.searchText != '') {
            queryParams['searchText'] = this.searchText;
        }

        // Publishing query params
        this.filtersApplied.emit(queryParams);

        // Constructing url
        let url: string = this.fetchUrl + '?';

        Object.keys(queryParams).forEach(param => {
            url += `${encodeURIComponent(param)}=${encodeURIComponent(queryParams[param])}&`;
        })

        return url;
    }

    setPaginationDetails(data: any): void {
        let records = this.processRecords(data.records);
        this.rows = records;

        // Publish refreshed data
        let refreshed = data;
        refreshed['records'] = records;
        this.refreshedData.emit(refreshed);

        this.totalRecords = data.totalRecords;
        if (!this.dataLoaded) {
            this.dataLoaded = true;
        }
        this.dataLoading = false;
    }

    processRecords(records: Array<Object>): Array<Object> {
        var selfData = this;
        records.forEach((record: any) => {
            //To handle the image columns
            if (selfData.imageColumns && selfData.imageColumns.length) {
                record = selfData.setImageData(record, selfData.imageColumns);
            }

            //To handle the colour buttons has boolean values
            if (selfData.colourButtonColumns && selfData.colourButtonColumns.length) {
                record = selfData.setColourButtonData(record, selfData.colourButtonColumns);
            }

            //To handle the date values
            if (selfData.dateColumns && selfData.dateColumns.length) {
                record = selfData.setDateFieldValue(record, selfData.dateColumns);
            }

        });
        return records;
    }

    setImageData(record: any, imageColumns: Array<Object>): any {
        imageColumns.forEach((columnName: any) => {
            if (record[columnName] && record[columnName] != '') {
                let path = record[columnName];
                if (path.substring(0, 4) != 'http') {
                    path = baseURL + 'uploads/' + path;
                }
                record[columnName] = '<img style="max-height: 30px;" src="' + path + '" />';
            }
        });
        return record;
    }

    setDateFieldValue(record: any, dateColumns: Array<Object>): any {
        dateColumns.forEach((column: any) => {
            let columnName = column.name;
            if (record[columnName] && record[columnName] != '') {
                let format = column.dateFormat;
                if (!format) {
                    format = 'yMMMd';
                }
                record[columnName] = this.datePipe.transform(record[columnName], format);
            }
        });
        return record;
    }

    setColourButtonData(record: any, colourButtonColumns: Array<Object>): any {
        colourButtonColumns.forEach((columnName: any) => {
            if (record[columnName]) {
                record[columnName] = 'Yes';//<div class="btn btn-success partner-status">Yes</div>';
            } else {
                record[columnName] = 'No';//<div class="btn btn-danger partner-status">No</div>';
            }
        });
        return record;
    }

    public changePage(page: any, data: Array<any> = this.data): void {
        this.page = page.page;
        this.startVal = (page.page - 1) * parseInt(page.itemsPerPage);
        this.endVal = this.startVal + parseInt(page.itemsPerPage);
    }

    public changeSort(data: any, config: any): any {
        if (!config.sorting) {
            return data;
        }

        let columns = this.config.sorting.columns || [];
        let columnName: string = void 0;
        let sort: string = void 0;

        for (let i = 0; i < columns.length; i++) {
            if (columns[i].sort === 'asc' || columns[i].sort === 'desc') {
                columnName = columns[i].name;
                sort = columns[i].sort;
            }
        }

        if (columnName) {
            let sign = '';
            if (sort == 'desc') {
                sign = '-';
            }
            this.sortColumnName = sign + columnName;
        } else {
            this.sortColumnName = '';
        }
        console.log(columnName + '-' + sort);
    }

    public changeFilter(data: any, config: any): any {
        this.columnFilter = [];
        this.isSearchEnabled = false;
        this.columns.forEach((column: any) => {
            if (column.filtering) {
                let searchText = column.filtering.filterString;
                this.columnFilter.push({ 'name': column.name, 'value': searchText });
                if (searchText != '') {
                    this.isSearchEnabled = true;
                }
            }
        });
    }

    public onChangeTable(config: any, page: any = { page: this.page, itemsPerPage: this.itemsPerPage }, type: string): any {

        if (config.filtering) {
            Object.assign(this.config.filtering, config.filtering);
        }

        if (config.sorting) {
            Object.assign(this.config.sorting, config.sorting);
        }

        if (type == 'column') {
            let filteredData = this.changeFilter(this.data, this.config);
            let sortedData = this.changeSort(filteredData, this.config);
            this.page = 1;
        }

        if (type == 'page') {
            this.changePage(page, []);
        }

        if (type == 'topSearch') {
            console.log(this.searchText);
        }

        this.getFilterValue(type)
    }

    public getFilterValue(type) {
        if (this.columnFilter.length > 0) {
            for (let i = 0; i < this.columnFilter.length; i++) {
                this.filterValues = this.addFilterValue(this.filterValues, this.columnFilter[i]['name'], this.columnFilter[i]['value']);

                Object.keys(this.constFilters).forEach(property => {
                    if(property == this.columnFilter[i]['name']) {
                        this.constFilters[property] = this.columnFilter[i]['value'];
                    }
                });
            }
        }

        // Adding constant query params
        Object.keys(this.constFilters).forEach(property => {
            this.filterValues = this.addFilterValue(this.filterValues, encodeURIComponent(property), encodeURIComponent(this.constFilters[property]))
        });
        // Adding column sort query params
        if (this.sortColumnName != '') {
            this.filterValues = this.addFilterValue(this.filterValues, "order_by", this.sortColumnName)
        }
        // Adding serach text query params
        if (this.searchText != '' || this.searchText == '') {
            this.filterValues = this.addFilterValue(this.filterValues, "searchText", this.searchText);
        }

        if (type == 'topSearch' || type == 'column') {
            this.startVal = 0;
            this.endVal = this.limit;
            this.page = 1;
        }

        this.fetchRecords(this.startVal, this.endVal);
    }
    // function to add the query params
    public addFilterValue(arrayValue, keyToCompare, valueToUpdate) {
        if (arrayValue.length > 0) {
            arrayValue.forEach((column: any, index) => {
                if (column.name == keyToCompare) {
                    arrayValue[index]['value'] = valueToUpdate;
                } else {
                    this.canAdd = this.canAddFilter(arrayValue, keyToCompare);
                    if (this.canAdd == true) {
                        arrayValue.push({ 'name': keyToCompare, 'value': valueToUpdate })
                    }
                }
            });
        } else {
            arrayValue.push({ 'name': keyToCompare, 'value': valueToUpdate })
        }
        return arrayValue;
    }
    // function to check wheather the filter is exist or not
    public canAddFilter(values, name) {
        this.canAdd = true;
        for (let i = 0; i < values.length; i++) {
            if (values[i]['name'] == name) {
                return false;
            }
        }
        return this.canAdd;
    }

    public onCellClick(data: any): any {
        console.log(data);
    }

    linkClicked(data: any): any {
        // Removing the old value
        localStorage.removeItem('filters');
        for (let i = 0; i < this.filterValues.length; i++) {
            if (this.filterValues[i]['name'] == 'partner_ids') {
                this.filterValues.splice(i, 1);
            }
        }
        // Storing the value in localStorage
        Object.keys(this.constFilters).forEach(property => {
            if (property == 'partner_ids') {
                this.value = JSON.parse(JSON.stringify(this.constFilters[property]));
            } else {
                this.value = encodeURIComponent(this.constFilters[property])
            }
            this.filterValues = this.addFilterValue(this.filterValues, encodeURIComponent(property), this.value)
        });
        let filterData: any = {
            'url': this.currentState, 'filter_value': this.filterValues,
            'start': this.startVal, 'end': this.endVal,
            'page': this.page, 'limit': this.itemsPerPage
        }
        localStorage.setItem('filters', JSON.stringify(filterData));
        this.event.emit({
            data: data
        });
    }

    public changeLimit(): void {
        console.log('Limit:' + this.limit);
        this.itemsPerPage = this.limit;
        this.page = 0;
        this.fetchRecords(0, this.itemsPerPage);
    }

    public navigateToAddScreen(): void {
        console.log('Redirecting to ' + this.addButtonInfo.url);
        this.router.navigate([this.addButtonInfo.url]);
    }

    private handleError(error: Response | any) {
        let errMsg: string;
        if (error instanceof Response) {
            const body = error.json() || '';
            const err = body.error || JSON.stringify(body);
            errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
        } else {
            errMsg = error.message ? error.message : error.toString();
        }
        console.error(errMsg);
        return Observable.throw(errMsg);
    }

    // Updating specific row datas
    @Input('updateRows')
    set updateRows(newRows: Array<Object>) {
        let pageData: Array<any> = [];
        this.rows.forEach(row => { pageData.push(row) });

        if (newRows) {
            newRows.forEach(row => {
                let rowIndex: number = pageData.map(item => item['id']).indexOf(row['id']);
                this.rows[rowIndex] = this.processRecords([row])[0];
            });
        }

        this.rows = pageData;
    }

    // Updating table data
    @Input('refreshRedTable')
    set refreshRedTable(data: any) {
        if (data) {
            if (data.mode == 'delete') {
                let recordsOnPage = this.totalRecords % this.itemsPerPage;
                if (recordsOnPage == 1 && this.page > 1) {
                    this.page = this.page - 1;
                }
            }
            this.refreshPage();
        }
    }

    // Updates records on ng2-table checkbox selections
    updateSelectedRecords(data: Array<any>) { this.selectedRecords = data; }

    @Output('export') exportRaw: EventEmitter<Array<any>> = new EventEmitter();

    // Exporting selected records
    exportSelectedRecords(format: string) {
        // Exporting as raw
        if (format == 'raw') this.exportRaw.emit(this.selectedRecords);
    }

    // Emits value, that changed by table cell inputs
    @Output('valueChanges') valueChanges: EventEmitter<any> = new EventEmitter();

    publishValueChanges(event: any) {
        this.valueChanges.emit(event);
    }

    ngOnDestroy() {
        Object.keys(name => {
            this.subscriptions[name].unsubscribe();
        })
    }
}

