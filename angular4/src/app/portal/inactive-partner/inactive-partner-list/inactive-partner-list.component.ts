import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { GetApiurl } from 'app/parameters';

@Component({
    selector: 'app-inactive-partner-list',
    templateUrl: './inactive-partner-list.component.html',
    styleUrls: ['./inactive-partner-list.component.scss']
})
export class InactivePartnerListComponent implements OnInit {

    public fetchUrl = GetApiurl("initial_partner_details/");
    public addButtonInfo: Object = {};
    public commonFilter: Object = {filterString: '', columnName:'company_name,email,city',
        placeholder: 'Search by partner name / Email / City'};
    public cols: Array<any> = [
        { title: 'Company name', name: 'company_name'},
        { title: 'Mobile', name: 'mobile', sort: false },
        { title: 'Email', name: 'email', sort: false},
        { title: 'City', name: 'city' },
        { title: 'Reg Date', name: 'created_at', dateFormat: 'yMMMd' },
        { title: 'Ext Partner', name: 'existing_status', sort: false, isColourButton: true},
        {title: 'Actions', links: ['View']},
    ];
    public backend_report_fetchUrl:string = GetApiurl('initial_partner_details/download_inactive_partner_list/')
    public reportFilters: Array<any> = [
    ];

    constructor(private router: Router) { }

    ngOnInit() {}

    eventListener(event: any) {
        if (event.data.action == 'View') {
            let url = "/app/inactive-partner/" + event.data['row']['id'] + "/activate";
            this.router.navigateByUrl(url);
        } else if (event.data.action == 'Delete') {
            // Todo: Don't forgot to add the refresh logic after delete
            console.log('delete');
        }
    }

}
