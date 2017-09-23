import { Component, OnInit, OnDestroy } from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {Subscription} from "rxjs/Rx";


import {UserService} from "../user.service";

@Component({
  selector: 'app-users-view',
  templateUrl: './users-view.component.html',
  styleUrls: ['./users-view.component.scss']
})
export class UsersViewComponent implements OnInit {
    private subscription:Subscription;
    private userdetail:any
    private usertype:any

   constructor(private service:UserService, private activatedRoute:ActivatedRoute){

   }


      ngOnInit() {
           this.subscription = this.activatedRoute.params.subscribe(
            (param: any) => {
                let id = param['id'];
                this.viewUser(id)
            })
    }


    private viewUser(id:any){
              this.service.getusers(id)
                .then(data=> {
                    this.userdetail = data[0];
                   localStorage.setItem('username', this.userdetail.username);
                    if(data[0].user_type == 'P'){

                    this.usertype='Partner'
                }
                  else if(data[0].user_type == 'R'){
                        this.usertype='Redington'
                    }

                    else if(data[0].user_type == 'C'){
                        this.usertype='customer'
                    }
                })
    }
      ngOnDestroy() {
        this.subscription.unsubscribe();
    }

}

