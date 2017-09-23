import { Component, OnInit } from '@angular/core';
import { GetApiurl } from 'app/parameters';
import { Router } from '@angular/router';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { PartnerService } from '../partner/partner.service';
import { GlobalsService } from 'app/services';
import { Partner } from '../partner/partner';
declare var jQuery: any;

@Component({
  selector: 'app-orc-linking',
  templateUrl: './orc-linking.component.html',
  styleUrls: ['./orc-linking.component.scss']
})
export class OrcLinkingComponent implements OnInit {

    customer: Partner = new Partner(-1,'',false,-1,'','',0,'','','','','','','',0,'','','','',[],[]);
    refreshRedTable: any;
    dealerCode: any = undefined;
    progress: string = undefined;
    process: string = undefined;
    recipientOptions: Array<{
          id: string;
          text: string;
      }> = [];
    remoteConfig: any = {
        url: GetApiurl('partner_details/search-partner/'),
        searchField: 'company_name',
        debounceTime: 500,
        authentication: true,
        tokenId: 'id_token',
        tokenStorage: 'localStorage',
        idField: 'id',
        textField: 'company_name'
    };
    orcLinkingForm: FormGroup;

    public fetchUrl = GetApiurl("partner_details/unlinked-customers/");
    public addButtonInfo: Object = {};
    public commonFilter: Object = {filterString: '', columnName:'company_name,email,city',
        placeholder: 'Search by Company name / Email / City'};
    public cols: Array<any> = [
        { title: 'Company name', name: 'company_name'},
        { title: 'Partner Code', name: 'orc_link_code', sort: false },
        { title: 'Email', name: 'email', sort: false},
        { title: 'City', name: 'city' },
        { title: 'Reg Date', name: 'created_at', dateFormat: 'yMMMd', sort: true },
        {title: 'Actions', links: ['Add', 'View', 'Delink']},
    ];
    public reportFilters: Array<any> = [
    ];

    constructor(private router: Router, private fb: FormBuilder, private service: PartnerService, private globalService: GlobalsService) { }

    ngOnInit() {
      this.buildForm();
      jQuery('#modal').modal('hide');
    }

    buildForm() {
        this.dealerCode = undefined;
        this.orcLinkingForm = this.fb.group({
                    'partner': ['', [ Validators.required ]],
                })
    }

    eventListener(event: any) {
        this.process = event.data.action;
        jQuery('#modal').modal('show');
        this.customer = event.data.row;
    }

    public selected(value: any): void {
        if(value) {
            this.service.getPartnerDetail(value['id']).subscribe(res => {
                this.dealerCode = res['jba_code']
            })
        } else {
            this.dealerCode = undefined;
        }
    }

    submit() {
        if(this.dealerCode != undefined) {
            this.progress = 'linking';
            this.service.customerLinkingService(this.orcLinkingForm.value, this.customer.id).then(res => {
                if (res) {
                    this.buildForm;
                    this.progress = undefined;
                    this.refreshRedTable = { mode: 'refresh', id: this.customer.id };
                    jQuery('#modal').modal('hide');
                    this.globalService.setToastMessage(this.customer.company_name+" linked with " + this.orcLinkingForm.controls['partner'].value[0]['text'], 5000);
                }
            })
        }
    }

    delink() {
        this.progress = 'delinking';
        this.service.customerDelinkingService(this.customer.id).then(res => {
            if (res) {
                this.progress = undefined;
                this.refreshRedTable = { mode: 'refresh', id: this.customer.id };
                jQuery('#modal').modal('hide');
                this.globalService.setToastMessage(this.customer.company_name+" delinked", 5000);
            }
        })
    }
    
    navigate() {
        let url = "/app/partner/" + this.customer.partner + "/details";
        this.router.navigateByUrl(url);
        jQuery('#modal').modal('hide');
    }

}
