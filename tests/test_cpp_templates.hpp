namespace geggo
{

template <class S>
class pair {
  S values[2];
  S first;
  S second;

public:
  //constructor
  pair (S first, S second);
  
  //method with template return type
  S get_first();
  S& get_second();

  //method with templated argument
  int is_first(S arg);

  int is_second(S& ref_arg);
  

};

pair<int> mypair(1,2);

template <class T>
T MAX (T a, T b)
{
  return (a>b?a:b);
}



typedef pair<int> intpair;

intpair first(intpair inpair);

}
