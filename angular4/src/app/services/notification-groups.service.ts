import { Injectable } from '@angular/core';
import { AuthHttp } from 'angular2-jwt';
import { Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';

import { GetApiurl } from 'app/parameters';
import { NotificationGroup } from 'app/classes';

@Injectable()
export class NotificationGroupsService {
    private defaultShowGroupIdSource = new BehaviorSubject<number>(null);
    defaultShowGroupId$ = this.defaultShowGroupIdSource.asObservable();


    constructor(private authHttp: AuthHttp) { }

    updateDefaultShowGroupId(id: number) { this.defaultShowGroupIdSource.next(id); }

    //Api call to Get list of notification groups
    getNfGroups() {
        let url = GetApiurl(`notification-groups/`);

        return this.authHttp
            .get(url)
            .map(Response => Response.json())
            .catch(this.handleError);
    }

    // Api call to create new notification group
    createNfGroup(object: NotificationGroup) {
        let url = GetApiurl(`notification-groups/`);

        return this.authHttp
            .post(url, JSON.stringify(object))
            .map(Response => Response.json())
            .catch(this.handleError);

    }

    // Api call to Edit notification group
    updateNfGroup(object: NotificationGroup) {
        let url = GetApiurl(`notification-groups/${object.id}/`);

        return this.authHttp
            .patch(url, JSON.stringify(object))
            .map(Response => Response.json())
            .catch(this.handleError);


    }

    // Api call to delete notification group
    deleteNfGroup(id: number) {
        let url = GetApiurl(`notification-groups/${id}/`);

        return this.authHttp
            .delete(url)
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
