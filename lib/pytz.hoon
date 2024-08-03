/*  pytz-data
:: helper structures and functions
::
=>  |%
    +$  dext     [i=@ud d=@da]  :: indexed time
    +$  delta    [sign=? d=@dr] :: positive or negative offset
    ::
    ++  apply-delta
      |=  [=time =delta]
      ^+  time
      (?:(sign.delta add sub) time d.delta)
    ::
    ++  invert-delta  |=(=delta delta(sign !sign.delta))
    ::
    ++  apply-invert-delta
      |=  [=time =delta]
      ^+  time
      (apply-delta time (invert-delta delta))
    ::
    ++  compose-deltas
      |=  [a=delta b=delta]
      ^-  delta
      ?:  =(sign.a sign.b)
        [sign.a (add d.a d.b)]
      ?:  (gte d.a d.b)
        [sign.a (sub d.a d.b)]
      [sign.b (sub d.b d.a)]
    ::
    ++  numb :: adapted from numb:enjs:format
      |=  a=@u
      ^-  tape
      ?:  =(0 a)  "0"
      %-  flop
      |-  ^-  tape
      ?:(=(0 a) ~ [(add '0' (mod a 10)) $(a (div a 10))])
    ::
    ++  monadic-parsing
      |%
      :: parser bind
      ::
      ++  bind  
        |*  =mold
        |*  [sef=rule gat=$-(mold rule)]
        |=  tub=nail
        =/  vex  (sef tub)
        ?~  q.vex  vex
        ((gat p.u.q.vex) q.u.q.vex)
      :: try to parse and advance only on success 
      ::
      ++  seek
        |*  sef=rule
        |=  tub=nail
        =+  vex=(sef tub)
        ?~  q.vex
          [p=p.vex q=[~ u=[p=~ q=tub]]]
        [p=p.vex q=[~ u=[p=[~ p.u.q.vex] q=q.u.q.vex]]]
      ::
      ++  exact-dem
        |=  n=@ud
        =|  digits=(list @ud)
        |-
        ?:  =(0 n)
          %-  easy
          %+  roll  (flop digits)
          =|([p=@ q=@] |.((add p (mul 10 q)))) :: code from +bass
        ;<  d=@ud  bind  dit
        $(n (dec n), digits [d digits])
      --
    --
:: timezone-specific structures and parsers
::
=>  |%
    +$  rule  [offset=delta name=@t]
    +$  zone  ((mop @da rule) lth)
    ++  zon   ((on @da rule) lth)
    ::
    ++  parse-data
      |=  rows=wain
      ^-  [@t (map @t wain)]
      ?>  ?=(^ rows)
      :-  i.rows
      %-  ~(gas by *(map @t wain))
      =/  contents=wain  t.rows
      |-
      ?~  contents
        ~
      =/  [lines=@ud name=@t]  (rash i.contents parse-zone-header)
      :-  [name (scag lines t.contents)]
      $(contents (slag lines t.contents))
    ::
    ++  parse-zone-header
      =,  monadic-parsing
      ;<  lines=@ud  bind  dem
      ;<  *          bind  ace
      ;<  name=tape  bind  (star prn)
      (easy [lines (crip name)])
    ::
    ++  parse-zone-rows
      |=  rows=wain
      ^-  (list [@da rule])
      ?>  ?=(^ rows)
      =/  contents=wain  t.rows
      |-
      ?~  contents
        ~
      :-  (rash i.contents parse-zone-row)
      $(contents t.contents)
    ::
    ++  parse-zone-row
      =,  monadic-parsing
      ;<  jump=@da   bind  parse-datetime
      ;<  *          bind  com
      ;<  =delta     bind  parse-offset
      ;<  *          bind  com
      ;<  name=@t    bind  (cook crip (star prn))
      (easy [jump delta name])
    ::
    ++  parse-datetime
      =,  monadic-parsing
      ;<  y=@ud   bind  (exact-dem 4)
      ;<  *       bind  hep
      ;<  mo=@ud  bind  (exact-dem 2)
      ;<  *       bind  hep
      ;<  d=@ud   bind  (exact-dem 2)
      ;<  *       bind  (just 'T')
      ;<  h=@ud   bind  (exact-dem 2)
      ;<  *       bind  col
      ;<  mi=@ud  bind  (exact-dem 2)
      =/  d=@da   (year [& y] mo d h mi 0 ~)
      ;<  col=(unit char)  bind  (seek col)
      ?~  col
        (easy d)
      ;<  s=@ud  bind  (exact-dem 2)
      =.  d      (add d (mul s ~s1))
      ;<  dot=(unit char)  bind  (seek dot)
      ?~  dot
        (easy d)
      ;<  f=@ud  bind  (exact-dem 3)
      (easy (add d (div (mul f ~s1) 1.000)))
    ::
    ++  parse-offset
      =,  monadic-parsing
      ;<  sign=?  bind  (cook |=(=@t =(t '+')) ;~(pose lus hep))
      ;<  h=@ud   bind  (exact-dem 2)
      ;<  *       bind  col
      ;<  m=@ud   bind  (exact-dem 2)
      (easy `delta`[sign (add (mul h ~h1) (mul m ~m1))])
    --
:: materialize the timezones
::
=/  [version=@t files=(map @t wain)]
  (parse-data (to-wain:format pytz-data))
=/  names=(list @t)  ~['UTC' 'America/New_York']
:: =/  names=(list @t)  ~(tap in ~(key by files))
=/  zones=(map @t zone)
  %-  ~(gas by *(map @t zone))
  =/  idx=@ud  1
  =/  total=@ud  (lent names)
  ^-  (list [@t zone])
  |-
  ?~  names
    ~&  >  "timezones were successfully loaded!"
    ~
  ~&  >>  "loading timezone [{(numb idx)}/{(numb total)}]: {(trip i.names)}"
  :_  $(idx +(idx), names t.names)
  :-  i.names
  %+  gas:zon  *zone
  %-  parse-zone-rows
  (~(got by files) i.names)
:: timezone conversion core
::
|%
++  zn
  |_  name=@t
  ++  zone   (~(got by zones) name)
  ::
  ++  active-rule
    |=  utc-time=@da
    ^-  (unit [@da rule])
    (ram:zon (lot:zon zone ~ `utc-time))
  ::
  ++  active-offset
    |=  utc-time=@da
    ^-  (unit delta)
    (bind (active-rule utc-time) (cork tail head))
  :: set of all offsets in the timezone
  ::
  ++  offsets
    ^-  (set delta)
    %-  ~(gas in *(set delta))
    %+  turn  (tap:zon zone)
    (cork tail head)
  ::
  ++  utc-to-tz
    |=  utc-time=@da
    ^-  (unit dext)
    ?~  off=(active-offset utc-time)
      ~
    =/  tz-time=@da  (apply-delta utc-time u.off)
    :: is this the first or second occurence of this tz-time?
    ::
    =/  times=(list @da)  (tz-to-utc-list tz-time)
    ?~  idx=(find [utc-time]~ times)
      ~
    [~ u.idx tz-time]
  ::
  ++  tz-to-utc
    |=  =dext
    ^-  (unit @da)
    :: generate all possible times
    ::
    =/  times=(list @da)  (tz-to-utc-list d.dext)
    :: return the time at the requested index
    ::
    ?:  (lte (lent times) i.dext)
      ~
    [~ (snag i.dext times)]
  :: time ordered list of valid candidates
  ::
  ++  tz-to-utc-list
    |=  tz-time=@da
    ^-  (list @da)
    |^
    (sort candidates lth)
    :: invert this time for all offsets of the timezone
    ::
    ++  candidates
      ^-  (list @da)
      %+  murn  ~(tap in offsets)
      |=  offset=delta
      ^-  (unit @da)
      =/  utc-candidate=@da  (apply-invert-delta tz-time offset)
      ?.  (validate utc-candidate offset)
        ~
      [~ utc-candidate]
    :: check whether a candidate could have been validly
    :: generated by the given offset
    ::
    ++  validate
      |=  [utc-time=@da offset=delta]
      ^-  ?
      ?~  off=(active-offset utc-time)
        %.n
      =(offset u.off)
    --
  ::
  ++  localize
    |=  utc-time=@da
    ^-  @da
    (tail (need (utc-to-tz utc-time)))
  ::
  ++  localize-soft
    |=  utc-time=@da
    ^-  (unit @da)
    (bind (utc-to-tz utc-time) tail)
  ::
  ++  universalize
    =|  idx=@ud
    |=  tz-time=@da
    ^-  @da
    (need (tz-to-utc idx tz-time))
  ::
  ++  universalize-soft
    =|  idx=@ud
    |=  tz-time=@da
    ^-  (unit @da)
    (tz-to-utc idx tz-time)
  --
--
