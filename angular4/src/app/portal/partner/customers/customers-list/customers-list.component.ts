import { Component, OnInit } from '@angular/core';
import {Router, ActivatedRoute, Params} from '@angular/router';
import { GlobalsService } from 'app/services';
import { Subscription } from 'rxjs/Subscription';
import { CustomersService } from 'app/services/customers.service'
declare var jQuery: any;

// Services
import {PartnerService} from "./../../partner.service";
import {GetApiurl} from "../../../../parameters";



@Component({
  selector: 'app-customers-list',
  templateUrl: './customers-list.component.html',
  styleUrls: ['./customers-list.component.scss']
})
export class CustomersListComponent implements OnInit {

    private subscription:Subscription;
    private partnerId:any;
    private getSub:any;
    private id:number;
    selectedId: number;

     constructor(private Service:PartnerService, private router: Router, private activatedRoute:ActivatedRoute,
                 private globals: GlobalsService, private customerService:CustomersService) {
          this.getSub = this.activatedRoute.parent.params.subscribe(params => {
           this.id = +params["id"];
       });

     }

    public length: number = 0;
    public fetchUrl: string;
    public addButtonInfo:Object;
    public commonFilter: Object = {filterString: '', columnName:'company_name,address,pan_number', placeholder: 'Search by Company name / Address / PAN'};
    public columns: Array<any> = [
        {title: 'Company name', name: 'company_name'},
        {title: 'Address', name: 'address'},
        {title: 'City', name: 'city'},
        {title: 'State', name: 'state'},
        {title: 'PAN', name: 'pan_number', sort: false},
        {title: 'Logo', name: 'logo', isImage: true, sort: false},
        {title: 'Actions', links: ['View']},
    ];

  ngOnInit() {
     this.fetchUrl = GetApiurl("customers/get_partner_customer/" + this.id + "/");

     this.subscription = this.globals.user$.subscribe(users => {
            if(users!=null){
                if (users.user_type=='R'){
                    this.columns[6].links=['View']
                }
                else if (users.user_type=='P'){
                    this.columns[6].links=['View','Edit','Delete']
                     this.addButtonInfo = {text: 'Add customer', url:  'app/partner/' + this.id + '/add_customer'};
                }
                else {
                    this.columns[6].links=['View']
                }
            }
        });

   }


  eventListener(event:any) {
      let id = event.data.row.id;
      this.selectedId = id;
        if (event.data.action == 'Edit') {
            let url:string;
             url = "/app/partner/" + this.id + "/customers/" + event.data['row']['id'] + "/edit";
            this.router.navigateByUrl(url);
        } else if (event.action == 'Delete') {
            this.customerService.checkIsDeletable(id).subscribe(data => {
                if(data) {
                    jQuery('#deleteModal').modal('show');
                } else {
                    jQuery('#warningModal').modal('show');
                }
            });
        }
        else if (event.data.action == 'View') {
            let url:string;
            if (event.data.row.id) {
                url = "/app/partner/" + this.id + "/customers/" + event.data['row']['id'] + "/view/details";

            }
            this.router.navigateByUrl(url)
        }
    }

    deleteCustomer() {
        this.customerService.deleteCustomer(this.selectedId).subscribe();
    }
}
