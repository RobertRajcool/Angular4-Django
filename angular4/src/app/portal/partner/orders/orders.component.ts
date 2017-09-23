import { Component, OnInit } from '@angular/core';
import { GetApiurl } from 'app/parameters';
import { Router } from "@angular/router";
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-orders',
    templateUrl: './orders.component.html',
    styleUrls: ['./orders.component.scss']
})
export class OrdersComponent implements OnInit {

    id: number;
    public fetchUrl: string;
    constructor(private activatedRoute:ActivatedRoute, private router:Router) {
        this.activatedRoute.parent.params.subscribe(params => {
            this.id = params["id"];
            this.fetchUrl = GetApiurl(`orders/partner/${this.id}/`);
        });
    }

    public addButtonInfo: Object = {};
    public commonFilter: Object = {};
    public columns: Array<any> = [
        {title: 'Order No', name: 'order_number', sort: false},
        {title: 'Customer name', name: 'customer__company_name', sort: false},
        {title: 'Product detail', name: 'details', sort: false},
        {title: 'Price', name: 'total_cost', sort: false},
        {title: 'Status', name: 'status', sort: false},
        {title: 'Actions', links: ['View']}
    ];

    ngOnInit() {
    }

    eventListener(event:any) {
        let data = event.data;
        if (data.action == 'View') {
            let url: string = "/app/orders/" + data.row.id;
            this.router.navigateByUrl(url);
        }
    }

}
