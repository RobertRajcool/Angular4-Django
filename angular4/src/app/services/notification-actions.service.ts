import { Injectable } from '@angular/core';
import { AuthHttp } from 'angular2-jwt';
import { Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { GetApiurl } from 'app/parameters';
import { NotificationGroup } from 'app/classes';

@Injectable()
export class NotificationActionsService {

    constructor(private authHttp: AuthHttp) { }

    // API call to fetch notification action details and unmapped list
    getFetchActionInfo(action: string) {
        let url = GetApiurl(`notification-actions/${ encodeURIComponent(action) }/fetch-details/`);

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // API call for assigning notificationGroup into notificationAction
    mapGroup(action: string, groud_id: number) {
        let url = GetApiurl(`notification-actions/map-group/`);
        let data = {
            'action': action,
            'group_id': groud_id
        };

        return this.authHttp
            .post(url, JSON.stringify(data))
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // API for removing notificationGroup from notificationAction
    unMap(action_id: number, groud_id: number) {
        let url = GetApiurl(`notification-actions/unmap-group/`);
        let data = {
            'action_id': action_id,
            'group_id': groud_id
        };

        return this.authHttp
            .post(url, JSON.stringify(data))
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
