import { Component, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { User } from '../user'
import { UserService } from '../user.service'
declare var jQuery: any;
import { Router } from '@angular/router';
import { GetApiurl } from 'app/parameters';

@Component({
    selector: 'app-userslist',
    templateUrl: './userslist.component.html',
    encapsulation: ViewEncapsulation.None,
    styleUrls: ['./userslist.component.scss']
})
export class UsersListComponent implements OnInit {
    users: User[] = [];
    refreshRedTable: any;
    public fetchUrl: string = GetApiurl('users/');
    public addButtonInfo: Object = {text: 'Add user', url:'/app/users/addUser'};
    public commonFilter: Object = {filterString: '', columnName:'username', placeholder: 'Search by Name / Email'};
    errorMessage: string;

    rows: Array<any> = [];
    columns: Array<any> = [
        { title: 'Name', name: 'full_name' },
        { title: 'Email', name: 'email', sort: false },
        { title: 'Type', name: 'user_type', sort: false },
        { title: 'Actions', links: ['View', 'Edit', 'Delete'] }
    ];

    deleteRow: any;
    modalVal: any;

    constructor(private userService: UserService, private router: Router) {}

    ngOnInit(): void {}

    deleteUser(index: number) {
        this.userService.deleteUser(index).subscribe(
            ng2TableData => {
                this.refreshRedTable = { mode: 'delete', id: index};
            }, // filter(row => row.id != index),
            error => this.errorMessage = error
        )
    }

    linkClicked(event: any, modal: any): any {
        let data = event.data;
        this.deleteRow = data;
        this.modalVal = modal;
        if (data.action == 'Edit') {
            let url: string = "/app/users/" + data['row']['id'];
            this.router.navigateByUrl(url);
        }
        else if(data.action=='View'){
          let url;
            if(data.row.id){
            url="/app/users/view/" + data['row']['id'];
            }
             this.router.navigateByUrl(url);
        }
        else if (data.action == 'Delete') {
            jQuery('#myModal').modal('show');
            //modal.open();
        }
    }

    public deleteUserClick() {
        this.deleteUser(this.deleteRow['row']['id']);
    }

}
