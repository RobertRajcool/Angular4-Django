import { Injectable } from '@angular/core';
import { AuthHttp } from 'angular2-jwt';
import { Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { GetApiurl } from 'app/parameters';
import { NotificationFilters } from 'app/classes';

@Injectable()
export class NotificationsService {

    constructor(private authHttp: AuthHttp) { }

    // Get filtered notifications
    getNotifications(filters: NotificationFilters) {
        let url = GetApiurl(`notifications/filter/?type=${ encodeURIComponent(filters.type) }&page_number=${filters.page_number}&records_per_page=${filters.records_per_page}&status=${ encodeURIComponent(filters.status) }`);

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // Mark notification as readed by current user
    markAsRead(id: number, filters: NotificationFilters) {
        let url = GetApiurl(`notifications/${id}/mark-as-read/`);
        let data = { 'filters': filters };

        return this.authHttp
            .post(url, JSON.stringify(data))
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // Mark notification as readed by current user
    markAsCompleted(id: number) {
        let url = GetApiurl(`notifications/${id}/mark-as-completed/`);

        return this.authHttp
            .get(url)
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
