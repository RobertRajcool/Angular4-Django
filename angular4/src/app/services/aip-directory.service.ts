import { Injectable } from '@angular/core';
import { Http, Response, Headers } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { GetApiurl } from 'app/parameters';

@Injectable()
export class AipDirectoryService {

    constructor(private http: Http) { }

    // Api call to filter locality details
    filterAip(filter_by: string, typo: string) {
        let url = GetApiurl(`aip-directory/filter/?filter_by=${ encodeURIComponent(filter_by) }&typo=${ encodeURIComponent(typo)}`);
        let headers = new Headers();
        headers.append('Content-Type', 'application/json');
        
        return this.http
            .get(url, { 'headers': headers })
            .map(Response => Response.json())
            .catch(this.handleError);

    }

    // Error handeling function
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

}
