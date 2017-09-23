import { Component, OnInit } from '@angular/core';
import { PartnerService } from '../partner/partner.service';
import { GlobalsService } from 'app/services/globals.service';

@Component({
  selector: 'app-partner-ratings-list',
  templateUrl: './partner-ratings-list.component.html',
  styleUrls: ['./partner-ratings-list.component.scss']
})
export class PartnerRatingsListComponent implements OnInit {
  ratings: any;
  counts: any;

  constructor(private service: PartnerService, private gs: GlobalsService) { }

  ngOnInit() {
    this.getRatings();
  }

  getRatings() {
    this.service.getRatings().then(res => {
      this.ratings = res;
      this.service.getRatingsCount().then(counts => {
        this.counts = counts;
      })
    })
  }

}
