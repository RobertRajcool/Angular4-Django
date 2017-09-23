import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, Params } from '@angular/router';

// Services
import { PartnerService } from './../partner.service';

// Directives
import { Activation, Partner } from './../partner';

@Component({
  selector: 'app-partner-list',
  templateUrl: './partner-view.component.html',
  styleUrls: ['./partner-view.component.scss']
})

export class PartnerViewComponent implements OnInit {
    
    scrn_var: string;
    screenName: any;
    partner: Partner = new Partner(-1,'',false,-1,'','',0,'','','','','','','',0,'','','','',[],[]);
    url: string;

    constructor(private service: PartnerService, private route: ActivatedRoute, private router: Router) {
      this.url = this.router.routerState.snapshot.url.substr(this.router.routerState.snapshot.url.lastIndexOf('/') + 1);
      this.screenName = (this.url.charAt(0).toUpperCase() + this.url.slice(1));
    }

    ngOnInit() {        
    }

}