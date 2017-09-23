import { Directive, Input, Output, AfterViewInit, ElementRef, EventEmitter } from '@angular/core';
import { Http, Headers } from '@angular/http';
import { FormControl } from '@angular/forms';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/debounceTime';

interface remoteConfigParams {
    url: string;
    searchField: string;
    debounceTime?: number;
    authentication: boolean;
    tokenId?: string;
    tokenStorage?: string;
    idField: string;
    textField: string;
    queryParams?: Object
}

@Directive({
    selector: '[extendNg2Select]',
    host: {
        '(typed)': 'listenTyping($event)',
    }
})
export class ExtendNg2SelectDirective {
    @Input('items') items: Array<any> = [];
    @Output() itemsChange: EventEmitter<any> = new EventEmitter();
    element: HTMLElement;
    @Input() remote: boolean = false;
    remoteConfig: remoteConfigParams = {
        url: '',
        searchField: 'id',
        debounceTime: 500,
        authentication: false,
        tokenId: 'id_token',
        tokenStorage: 'localStorage',
        idField: 'id',
        textField: 'text'
    };
    search_text: FormControl = new FormControl();
    apiCallSubscription: any;

    constructor(
        private http: Http,
        private el_ref: ElementRef,
    ) {
        this.element = this.el_ref.nativeElement;

    }

    @Input('remoteConfig')
    set remoteConfigData(data: remoteConfigParams) {
        if (data instanceof Object) {
            this.remoteConfig = data;
        }
    }


    // Listen search typing
    listenTyping(typed) {
        this.search_text.setValue(typed);
        this.search_text.updateValueAndValidity();
    }

    ngAfterViewInit() {
        // Add Search listener if remote search is enabled
        if (this.remote) {
            this.search_text.valueChanges
                .debounceTime(500)
                .subscribe(
                search_text => {
                    if (search_text) {
                        this.loadRemoteData(search_text);
                    }
                });
        }
    }

    // Load data from remote
    loadRemoteData(text: string) {
        let headers = new Headers();
        headers.append('Content-Type', 'application/json');
        if (this.remoteConfig.authentication && (this.remoteConfig.tokenStorage == 'localStorage')) {
            headers.append('Authorization', 'JWT ' + localStorage.getItem(this.remoteConfig.tokenId));
        }

        let url: string = this.remoteConfig.url;

        let qParams: Object = this.remoteConfig.queryParams;
        if (qParams) {
            url += '?';
            Object.keys(qParams).forEach(property => {
                url += `${encodeURIComponent(property)}=${encodeURIComponent(qParams[property])}&`;
            })
        }


        let data = JSON.stringify({ 'search_text': text, 'search_field': this.remoteConfig.searchField });

        if (this.apiCallSubscription) this.apiCallSubscription.unsubscribe();

        this.apiCallSubscription = this.http
            .post(url, data, { 'headers': headers })
            .map(Response => {
                let result: Array<any> = Response.json();
                let list: Array<any> = [];
                result.forEach(item => {
                    list.push({ id: item[this.remoteConfig.idField], text: item[this.remoteConfig.textField] })
                });
                return list;
            })
            .subscribe((list) => {
                this.itemsChange.emit(list);
            });
    }

}
