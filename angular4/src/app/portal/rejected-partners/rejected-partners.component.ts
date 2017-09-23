import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { GetApiurl } from 'app/parameters';
import {PartnerService} from "app/services/";
declare var jQuery: any;


@Component({
  selector: 'app-rejected-partners',
  templateUrl: './rejected-partners.component.html',
  styleUrls: ['./rejected-partners.component.scss']
})
export class RejectedPartnersComponent implements OnInit {
  public rejectReason;
  public fetchUrl = GetApiurl("rejected-partner-details/");
  public commonFilter: Object = {filterString: '', columnName:'company_name,email,city',
        placeholder: 'Search by partner name / Email / City'};
  public cols: Array<any> = [
        { title: 'Company name', name: 'company_name'},
        { title: 'Mobile', name: 'mobile', sort: false },
        { title: 'Email', name: 'email', sort: false},
        { title: 'City', name: 'city' },
        { title: 'Reg Date', name: 'created_at', dateFormat: 'yMMMd' },
        { title: 'Ext Partner', name: 'existing_status', sort: false, isColourButton: true},
        {title: 'Actions', links: ['View', 'Delete']},
    ];
  public selectedId: number = 0;
  refreshRedTable: any;
  saving: boolean = false;
  public backend_report_fetchUrl:string = GetApiurl('rejected-partner-details/download-rejected-partner-export-excel/')
    public reportFilters: Array<any> = [
      ];

  constructor(private partneService:PartnerService) { }

  ngOnInit() {

  }
  eventListener(event:any){
    if(event.data.action==='View'){
      let id=event.data['row']['id']
      this.partneService.partnerRejectView(id)
        .then(result=>{
         this.rejectReason=result[0].rejection_reason
          jQuery('#rejectViewModal').modal('show');
      })
    }
    if(event.data.action == 'Delete') {
      this.selectedId=event.data['row']['id']
      jQuery('#delete_partner').modal('show');
    }

  }

  deletePartner(){
        this.saving = true;
        this.partneService.deletePartner(this.selectedId).then(resp=>{
          if(resp) {
            this.saving = false;
            jQuery('#delete_partner').modal('hide');
            this.refreshRedTable = { mode: 'refresh', id: this.selectedId};
          }
        })
    }

}
