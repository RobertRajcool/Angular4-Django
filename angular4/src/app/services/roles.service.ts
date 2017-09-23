import { Injectable } from '@angular/core';
import { AuthHttp } from 'angular2-jwt';
import { Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

import { GetApiurl } from 'app/parameters';
import { Roles } from 'app/classes';
import { RolesList } from 'app/classes/roles';

@Injectable()
export class RolesService {

  constructor(private authHttp: AuthHttp) { }

  // Api call to get list of roles created by the authenticated user
  getRoles(): Observable<Roles[]> {
    let url = GetApiurl(`roles/`);

    return this.authHttp
      .get(url)
      .map(Response => Response.json())
      .catch(this.handleError)
  }

  // Api call to create new role
  createRole(role: Roles): Observable<Roles> {
    let url = GetApiurl(`roles/`);

    return this.authHttp
      .post(url, JSON.stringify(role))
      .map(Response => Response.json())
      .catch(this.handleError)
  }

  // Api call to get details of the selected role
  getRole(id: string): Observable<Roles> {
    let url = GetApiurl(`roles/${id}/`);

    return this.authHttp
      .get(url)
      .map(Response => Response.json())
      .catch(this.handleError)
  }

  // Api call to update the details of the selected role
  updateRole(role: Roles): Observable<Roles> {
    let url = GetApiurl(`roles/${role.id}/`);

    return this.authHttp
      .patch(url, JSON.stringify(role))
      .map(Response => Response.json())
      .catch(this.handleError)
  }

  // Api call to delete selected role
  deleteRole(id: string): Observable<Roles> {
    let url = GetApiurl(`roles/${id}/`);

    return this.authHttp
      .delete(url)
      .map(Response => Response.json())
      .catch(this.handleError)
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

  getRolesList(): Observable<Roles> {
      let url = GetApiurl(`roles/`);

    return this.authHttp
      .get(url)
      .map(this.extractRoles)
      .catch(this.handleError)
  }

  private extractRoles(res:Response) {
    let rolesBody = res.json();
      let rolesArray: RolesList[] = [];
      for (let rBody of rolesBody) {
          let roles:RolesList = new RolesList(          
          rBody.id,
          rBody.alias);
          rolesArray.push(roles);    
      }
      return rolesArray;
  }
}
