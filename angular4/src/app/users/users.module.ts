import { UsersComponent } from './users.component';
import { AddUserComponent } from './adduser.component';
import { EditUserComponent } from './edituser.component';
import { UserRouting } from './users.routing';
import { UserService } from './user.service';

import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import  { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UsersListComponent } from './userslist/userslist.component';
import { RolesComponent } from './roles/roles.component';
import 'parsleyjs';
import { PaginationModule } from 'ng2-bootstrap';
import { Ng2TableModule } from 'ng2-table/ng2-table';
import { SelectModule } from 'ng2-select';    // This module is used for multiple select dropdown (ng-select)
import { Select2Module } from 'ng2-select2';  // This module is used for default select dropdown (select2)
import { ModalModule } from 'ng2-modal';
import { AlertModule } from 'ng2-bootstrap';
import { UsersViewComponent } from './users-view/users-view.component';
import { SharedModule } from "app/shared";


@NgModule({
  declarations: [
    UsersComponent,
    AddUserComponent,
    EditUserComponent,
    UsersListComponent,
    RolesComponent,
    UsersViewComponent
  ],
  imports: [
    CommonModule,
    UserRouting,
    FormsModule,
    ReactiveFormsModule,
    ModalModule,
    Ng2TableModule,
    PaginationModule.forRoot(),
    SelectModule,
    Select2Module,
    PaginationModule.forRoot(),
      AlertModule.forRoot(),
      SharedModule
  ],
  providers: [
    UserService
  ],
})
export class UsersModule { }
