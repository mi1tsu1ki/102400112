#include<iostream>
using namespace std;
#include<stdexcept>

typedef struct LNode{
    int data;
    struct LNode* next;
}LNode, *LinkList;

bool InitList(LinkList &L){
    L=new LNode;
    if(L==NULL)
        return false;
    L->next=NULL;
    return true;
}

bool Empty(LinkList L){
    return (L->next==NULL);
}

bool InsertNextNode(LNode* p,int e){
    if(p==NULL)
        return false;
    LNode* s=new LNode;
    s->data=e;
    s->next=p->next;
    p->next=s;
    return true;
}

bool ListInsert(LinkList &L,int i,int e){
    if(i<1)
        return false;
    LNode* p;
    int j=0;
    p=L;
    while(p!=NULL && j<i-1){
        p=p->next;
        j++; 
    }
    return InsertNextNode(p,e);
}

bool InsertPriorNode(LNode* p,int e){
    if(p==NULL)
        return false;
    LNode* s=new LNode;
    s->next=p->next;
    p->next=s;
    s->data=p->data;
    p->data=e;
    return true;
}

bool ListDelete(LinkList &L,int i,int &e){
    if(i<1)
        return false;
    LNode *p;
    int j=0;
    p=L;
    while(p!=NULL && j<i-1){
        p=p->next;
        j++;
    }
    if(p==NULL)
        return false;
    if(p->next==NULL)
        return false;
    LNode* q=p->next;
    e=q->data;
    p->next=q->next;
    delete q;
    return true;
}

bool DeleteNode(LNode* p){
    if(p==NULL)
        return false;
    LNode* q=p->next;
    p->data=q->data;
    p->next=q->next;
    delete q;
    return true;
}

void test(){
    LinkList L;
    InitList(L);
    ListInsert(L,1,1);
}

int main(){
    test();

    return 0;
}