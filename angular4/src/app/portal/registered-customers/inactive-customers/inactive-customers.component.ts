import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { GetApiurl } from 'app/parameters';

@Component({
  selector: 'app-inactive-customers',
  templateUrl: './inactive-customers.component.html',
  styleUrls: ['./inactive-customers.component.scss']
})
export class InactiveCustomersComponent implements OnInit {

    public fetchUrl = GetApiurl("initial_partner_details/inactive-customers/");
    public addButtonInfo: Object = {};
    public commonFilter: Object = {filterString: '', columnName:'company_name,email,city',
        placeholder: 'Search by customer name / Email / City'};
    public cols: Array<any> = [
        { title: 'Company name', name: 'company_name'},
        { title: 'Mobile', name: 'mobile', sort: false },
        { title: 'Email', name: 'email', sort: false},
        { title: 'City', name: 'city' },
        { title: 'Reg Date', name: 'created_at', dateFormat: 'yMMMd' },
        {title: 'Actions', links: ['View']},
    ];
    public reportFilters: Array<any> = [
    ];

    constructor(private router: Router) { }

  ngOnInit() {
  }

  eventListener(event: any) {
        if (event.data.action == 'View') {
            let url = "/app/partner-customers/" + event.data['row']['id'] + "/activate";
            this.router.navigateByUrl(url);
        }
    }

}
