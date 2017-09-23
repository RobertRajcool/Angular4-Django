export class Notifications {
    url: string;
    id: number;
    type: string;
    subject: string;
    object_id: string;
    details: Object;
    recipients: string;
    purpose: string;
    status: string;
    posted_by: string;
    posted_at: Date;
    viewed_by: string;
    completed_by: string;
    completed_at: string;
}

export interface NotificationFilters {
    type?: string;
    page_number: number;
    records_per_page: number;
    status?: string;
}

// Notification groups
export class NotificationGroup {
    url: string;
    id: number;
    name: string;
    actions?: string;
    description: string;
    recipients: Array<string>;
    non_user_recepients: EmailRecepients;
    created_by: string;
    created_at: Date;
    updated_by: string;
    updated_at: Date;
}

export interface EmailRecepients {
    id?: string;
    name: string;
    email: string;

}

// Notification actions
export class NotificationAction {
    url: string;
    id: number;
    action: string;
    groups: Array<NotificationGroup>;
    created_by: string;
    created_at: Date;
    updated_by: string;
    updated_at: Date;
}