#include <map>
#include <iostream>

using namespace std;

int main()
{
    map<int, int> mymap;
    mymap.insert({1,11});
    mymap.insert({2,22});
    mymap.insert({3,33});
    mymap.insert({4,44});

    mymap.find(1);

    if(mymap.find(2) == mymap.end())
        cout << "not found";
}