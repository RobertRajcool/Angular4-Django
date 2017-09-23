import { Component, OnInit } from '@angular/core';
import { CustomersService } from 'app/services/customers.service'
import {Router} from "@angular/router";
import { GetApiurl } from 'app/parameters';
import { GlobalsService } from 'app/services/globals.service';
declare var jQuery: any;

@Component({
    selector: 'app-customers-list',
    templateUrl: './customers-list.component.html',
    styleUrls: ['./customers-list.component.scss']
})
export class CustomersListComponent implements OnInit {
    public customerid:any;
    selectedId: number;
    refreshRedTable: any;
    user: any;

    constructor(private customerService:CustomersService, private router: Router, private gs:GlobalsService) { }

    public fetchUrl: string = GetApiurl('customers/');
    public addButtonInfo: Object = {};
    public commonFilter: Object = {filterString: '', columnName:'company_name,address', placeholder: 'Search by Company name / Address'};
    public columns: Array<any> = [
        {title: 'Company name', name: 'company_name'},
        {title: 'Address', name: 'address'},
        {title: 'City', name: 'city'},
        {title: 'State', name: 'state'},
        //{title: 'PAN', name: 'pan_number'},
        {title: 'Partner', name: 'partner_name', sort: false},
        {title: 'Logo', name: 'logo', isImage: true, sort: false},
        {title: 'Actions', links: ['View', 'Edit', 'Delete']},
    ];

    ngOnInit() {
        this.gs.user$.subscribe(user => {
            this.user = user;
            if (this.user != null) {
              if (this.user.user_type && user.user_type == 'P') {
                this.addButtonInfo = {text: 'Add customer', url: '/app/customers/add'};
                let newList: Array<any> = [];
                this.columns.forEach((record: any) => {
                  if (record.name != 'partner_name') {
                    newList.push(record)
                  }
                });
                this.columns = newList;
              }
            }
        });
    }

    eventListener(event:any) {
        let data = event.data;
        let action = data.action;
        let id = data.row.id;
        this.selectedId = id;
        if (action == 'Edit') {
            let url:string;
            if (id) {
                url = "/app/customers/" + event.data['row']['id'] + "/edit";
            }
            this.router.navigateByUrl(url);
        } else if (action == 'View') {
            let url:string;
            if (id) {
                url = "/app/customers/" + event.data['row']['id'] + "/details";
            }
            this.router.navigateByUrl(url);
        } else if(action == 'Delete') {
            this.customerService.checkIsDeletable(id).subscribe(data => {
                if(data) {
                    jQuery('#deleteModal').modal('show');
                } else {
                    jQuery('#warningModal').modal('show');
                }
            });
        }
    }

    deleteCustomer() {
        this.customerService.deleteCustomer(this.selectedId).subscribe(resp=>{
            this.refreshRedTable = { mode: 'delete', id: this.selectedId};
        });
    }
}
