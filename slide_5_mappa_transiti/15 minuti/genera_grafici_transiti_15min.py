#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot di slide 5 sulla griglia quartoraria, usando il CSV derivato dagli XML.

Produce nuove versioni di barre giornaliere A09, linee A09/A11, macrozona,
produzione+net import, surplus adj zonale e surplus adj macrozonale.
Il grafico Sud-CentroSud/NTC resta quello orario nella cartella originale.
"""
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
TRANSITS = HERE / "dati" / "transiti_48h_15min.csv"
PRICE_CSV = PROJECT / "slide_2_scelta_evento_p_zero" / "15 minuti" / "dati" / "prezzi_zonali_15min_48h.csv"
PRODUCTION_DIR = PROJECT / "slide_4_carico_production"
LOAD_CSV = PRODUCTION_DIR / "dati" / "carico_produzione_48h.csv"
OUT = HERE / "grafici"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PRODUCTION_DIR))
from plot_produzione import read_production_and_load, NET_COLOR, NET_LABEL
from plot_surplus_macrozone import read_macrozone_series

ZONES = ["IT Sud", "IT Calabria", "IT Sicilia"]
ZERO_ZONES = set(ZONES)
DISPLAY = {"IT Sud": "Sud", "IT Calabria": "Calabria", "IT Sicilia": "Sicilia",
           "IT Centro-Sud": "Centro-Sud", "Grecia": "Grecia", "Malta": "Malta"}
NEIGHBOR_COLORS = {"IT Centro-Sud": "#1f77b4", "IT Calabria": "#ff7f0e",
                   "IT Sicilia": "#2ca02c", "Grecia": "#9467bd", "Malta": "#8c564b"}
SOURCE_COLORS = {"solare": "#f2c14e", "eolico": "#4c9f70", "resto": "#8d9db6"}
SOURCE_COLORS = {"solare": "#f2c14e", "eolico": "#4c9f70", "resto": "#8d9db6"}
MACRO = set(ZONES)


def load_inputs():
    if not TRANSITS.is_file():
        raise SystemExit("CSV transiti non trovato; esegui prima prepara_transiti_15min.py")
    if not PRICE_CSV.is_file():
        raise SystemExit("CSV prezzi non trovato; esegui prima slide 2/15 minuti/genera_prezzi_15min.py")
    flows = pd.read_csv(TRANSITS)
    flows["ts"] = pd.to_datetime(flows["timestamp_utc"], utc=True)
    prices = pd.read_csv(PRICE_CSV)
    prices["ts"] = pd.to_datetime(prices["timestamp_utc"], utc=True)
    zero_map = {z: pd.DatetimeIndex(prices.loc[prices[DISPLAY[z]] == 0, "ts"]) for z in ZONES}
    load, gen, netgen = read_production_and_load(str(LOAD_CSV))
    load.index = load.index.tz_convert("UTC")
    netgen.index = netgen.index.tz_convert("UTC")
    gen = gen.reset_index()
    gen["ts"] = pd.to_datetime(gen["ts"], utc=True)
    gen = gen.set_index(["zone", "ts"]).sort_index()
    # Raw tidy values used by the original stacked production/net-import chart.
    raw = pd.read_csv(LOAD_CSV)
    raw["ts"] = pd.to_datetime(raw["timestamp_utc"], utc=True)
    return flows, prices, zero_map, load, gen, netgen, raw


def net_import_zonal(flows, zone, times):
    inc = flows[flows.in_zone == zone].groupby("ts").flow_physical_mw.sum(min_count=1).reindex(times)
    out = flows[flows.out_zone == zone].groupby("ts").flow_physical_mw.sum(min_count=1).reindex(times)
    return inc.fillna(0) - out.fillna(0)


def zero_ticks(ax, times):
    if len(times):
        ax.scatter(times, np.zeros(len(times)), marker="|", color="#c00000", s=70,
                   linewidths=1.2, zorder=8, clip_on=False,
                   transform=ax.get_xaxis_transform())


def style_time(ax, labels=False, hours=(0, 6, 12, 18)):
    ax.xaxis.set_major_locator(mdates.DayLocator(tz="UTC"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m", tz="UTC"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=list(hours), tz="UTC"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M", tz="UTC"))
    ax.tick_params(axis="x", which="both", labelbottom=labels, length=3)
    if labels:
        for lab in ax.get_xticklabels(minor=True):
            lab.set_fontsize(7); lab.set_rotation(45); lab.set_ha("right")


def plot_lines(flows, zero_map):
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), dpi=150, sharex=True)
    for ax, zone in zip(axes, ZONES):
        zero_ticks(ax, zero_map[zone])
        neighbors = sorted(set(flows.loc[flows.out_zone == zone, "in_zone"]) |
                           set(flows.loc[flows.in_zone == zone, "out_zone"]))
        for nb in neighbors:
            d = flows[(flows.out_zone == nb) & (flows.in_zone == zone)].sort_values("ts")
            if d.scheduled_mw.notna().any():
                ax.plot(d.ts, d.scheduled_mw, color=NEIGHBOR_COLORS.get(nb, "#888"), lw=1.0,
                        label="Import %s (A09)" % DISPLAY.get(nb, nb))
        for nb in neighbors:
            d = flows[(flows.out_zone == zone) & (flows.in_zone == nb)].sort_values("ts")
            if d.scheduled_mw.notna().any():
                ax.plot(d.ts, d.scheduled_mw, color=NEIGHBOR_COLORS.get(nb, "#888"), lw=1.0,
                        ls="--", label="Export %s (A09)" % DISPLAY.get(nb, nb))
        times = pd.DatetimeIndex(sorted(flows.ts.unique()))
        ax.plot(times, net_import_zonal(flows, zone, times), color="black", lw=1.8,
                label="Import netto fisico (A11)", zorder=5)
        ax.axhline(0, color="#555", lw=.7, ls=":")
        ax.set_title(DISPLAY[zone], fontweight="bold"); ax.set_ylabel("MW")
        ax.grid(axis="y", color="#e3e3e3", lw=.4); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        ax.legend(loc="upper left", fontsize=7, ncol=2, frameon=True)
    style_time(axes[-1], labels=True)
    fig.suptitle("Import / Export / Net import per zona - intervalli 15 minuti (UTC)", fontweight="bold")
    fig.tight_layout(rect=[0,0,1,.98])
    path=OUT/"import_export_linee_48h_15min.png"; fig.savefig(path,dpi=150,bbox_inches="tight");plt.close(fig);print("scritto:",path)


def plot_daily_bars(flows):
    f=flows.copy(); f["delivery_date"]=pd.to_datetime(f.timestamp_local).dt.strftime("%Y-%m-%d")
    for day in ["2026-11-12","2026-11-13"]:
        d=f[f.delivery_date==day]
        fig,axes=plt.subplots(1,3,figsize=(15,5),dpi=150)
        for ax,z in zip(axes,ZONES):
            nbs=sorted(set(d.loc[d.out_zone==z,"in_zone"])|set(d.loc[d.in_zone==z,"out_zone"]))
            im=[];ex=[]
            for nb in nbs:
                a=d[(d.out_zone==nb)&(d.in_zone==z)].scheduled_mw.sum(min_count=1)
                b=d[(d.out_zone==z)&(d.in_zone==nb)].scheduled_mw.sum(min_count=1)
                im.append(0 if pd.isna(a) else a*.25);ex.append(0 if pd.isna(b) else b*.25)
            x=np.arange(len(nbs));w=.25; im=np.array(im); ex=np.array(ex)
            ax.bar(x-w,im,w,color="#2e8b57",alpha=.35,edgecolor="#2e8b57",label="Import A09")
            ax.bar(x,-ex,w,color="#c00000",alpha=.35,edgecolor="#c00000",label="Export A09")
            ax.bar(x+w,im-ex,w,color="#1f77b4",alpha=.35,edgecolor="#1f77b4",label="Saldo programmato")
            ax.set_xticks(x);ax.set_xticklabels([DISPLAY.get(n,n) for n in nbs],rotation=30,ha="right",fontsize=8)
            ax.set_title(DISPLAY[z],fontweight="bold");ax.set_ylabel("MWh")
            ax.axhline(0,color="#555",lw=.7);ax.grid(axis="y",color="#ddd",lw=.4)
            ax.spines["top"].set_visible(False);ax.spines["right"].set_visible(False)
        axes[0].legend(fontsize=7)
        fig.suptitle("Scambi commerciali A09 - %s - energia per confine (15 min)"%day,fontweight="bold")
        fig.tight_layout();path=OUT/("import_export_%s_15min.png"%day.replace("-",""));fig.savefig(path,dpi=150,bbox_inches="tight");plt.close(fig);print("scritto:",path)


def plot_macrozone(flows, zero_map):
    fig,ax=plt.subplots(figsize=(14,7),dpi=150)
    colors={"IT Centro-Sud":"#1f77b4","Grecia":"#9467bd","Malta":"#8c564b"}
    for nb in ["IT Centro-Sud","Grecia","Malta"]:
        inc=flows[(flows.out_zone==nb)&(flows.in_zone.isin(MACRO))].groupby("ts").scheduled_mw.sum(min_count=1)
        out=flows[(flows.out_zone.isin(MACRO))&(flows.in_zone==nb)].groupby("ts").scheduled_mw.sum(min_count=1)
        if inc.notna().any():ax.plot(inc.index,inc.values,color=colors[nb],lw=1.2,label="Import %s (A09)"%DISPLAY.get(nb,nb))
        if out.notna().any():ax.plot(out.index,out.values,color=colors[nb],lw=1.2,ls="--",label="Export %s (A09)"%DISPLAY.get(nb,nb))
    ext=flows[((flows.in_zone.isin(MACRO))&(~flows.out_zone.isin(MACRO)))|((flows.out_zone.isin(MACRO))&(~flows.in_zone.isin(MACRO)))].copy()
    ext["signed"]=np.where(ext.in_zone.isin(MACRO),ext.flow_physical_mw,-ext.flow_physical_mw)
    net=ext.groupby("ts").signed.sum(min_count=1)
    ax.plot(net.index,net.values,color="black",lw=2,label="Net import fisico macrozona (A11)")
    ticks=sorted(set().union(*(set(zero_map[z]) for z in ZONES)));zero_ticks(ax,pd.DatetimeIndex(ticks))
    ax.axhline(0,color="#555",lw=.7,ls=":");ax.set_ylabel("MW");ax.grid(axis="y",color="#ddd",lw=.4)
    ax.legend(loc="upper left",fontsize=8,ncol=2);style_time(ax,labels=True)
    ax.set_title("Macrozona Sud + Calabria + Sicilia - flussi esterni a 15 min (UTC)",fontweight="bold")
    fig.tight_layout();path=OUT/"macrozone_48h_15min.png";fig.savefig(path,dpi=150,bbox_inches="tight");plt.close(fig);print("scritto:",path)


def plot_production_netimport(flows, zero_map, load, gen, netgen, raw):
    fig,axes=plt.subplots(2,2,figsize=(14,8),dpi=150)
    for idx,z in enumerate(ZONES):
        r,c=divmod(idx,2);ax=axes[r,c]
        if z in gen.index.get_level_values("zone"):
            g=gen.loc[z].reindex(index=load.index,columns=list(SOURCE_COLORS)).fillna(0)
            ax.stackplot(load.index,*g[list(SOURCE_COLORS)].to_numpy().T,colors=list(SOURCE_COLORS.values()),alpha=.9)
            total=g.sum(axis=1).to_numpy()
        else: total=np.zeros(len(load))
        if z in load.columns: ax.plot(load.index,load[z],color="black",lw=1.4,label="Carico A65",zorder=5)
        if z in ZERO_ZONES:
            net=net_import_zonal(flows,z,load.index).fillna(0).to_numpy()
            net_a75=netgen[z].reindex(load.index).fillna(0).to_numpy()
            ax.plot(load.index,net_a75,color=NET_COLOR,lw=1.6,ls="--",label=NET_LABEL,zorder=7)
            ax.fill_between(load.index,net_a75,net_a75+net,color="#87ceeb",alpha=.7,edgecolor="#4682b4",lw=.5,label="Import netto A11",zorder=6)
        zero_ticks(ax,zero_map.get(z,[]));ax.set_title(DISPLAY.get(z,z),fontweight="bold");ax.set_ylabel("MW")
        ax.spines["top"].set_visible(False);ax.spines["right"].set_visible(False);ax.margins(x=0);ax.tick_params(axis="x",labelbottom=False)
    ax=axes[1,1];ax.axis("off")
    handles=[Patch(facecolor=SOURCE_COLORS[k],label=lab) for k,lab in [("solare","Solare A75"),("eolico","Eolico A75"),("resto","Resto A75")]]
    handles += [Line2D([0],[0],color="black",label="Carico A65"),Line2D([0],[0],color=NET_COLOR,ls="--",label=NET_LABEL),Patch(facecolor="#87ceeb",edgecolor="#4682b4",label="Import netto A11"),Line2D([0],[0],color="#c00000",marker="|",lw=0,markersize=8,label="Prezzo zero MGP")]
    ax.legend(handles=handles,loc="upper center",fontsize=8,frameon=False,bbox_to_anchor=(.5,.95))
    ax.text(.98,.02,"Dati A65/A75 e flussi: 15 min\nA11 Grecia: nativo PT60, gradino orario",ha="right",va="bottom",fontsize=7,transform=ax.transAxes,bbox=dict(boxstyle="round,pad=.25",fc="white",ec="#ccc",lw=.6))
    style_time(axes[1,0],labels=True)
    fig.suptitle("Produzione, carico e net import - 15 min UTC",fontweight="bold")
    fig.tight_layout(rect=[0,0,1,.97]);path=OUT/"produzione_netimport_3zone_15min.png";fig.savefig(path,dpi=150,bbox_inches="tight");plt.close(fig);print("scritto:",path)


def plot_surplus_adj(flows, zero_map, load, netgen):
    fig,axes=plt.subplots(2,2,figsize=(14,8),dpi=150)
    for idx,z in enumerate(ZONES):
        r,c=divmod(idx,2);ax=axes[r,c]
        l=load[z].fillna(0); p=netgen[z].reindex(load.index).fillna(0); ni=net_import_zonal(flows,z,load.index).fillna(0); available=p+ni; balance=available-l
        ax.plot(load.index,l,color="black",lw=1.4,label="Carico A65")
        ax.plot(load.index,available,color=NET_COLOR,lw=1.7,ls="--",label=NET_LABEL + " + import netto A11")
        ax.fill_between(load.index,available,l,where=balance>0,color="#2e8b57",alpha=.3,label="Surplus adj",interpolate=True)
        ax.fill_between(load.index,available,l,where=balance<0,color="#c00000",alpha=.3,label="Deficit adj",interpolate=True)
        zero_ticks(ax,zero_map.get(z,[]));ax.set_title(DISPLAY[z],fontweight="bold");ax.set_ylabel("MW")
        ax.set_yticks(range(0,6001,1000));ax.set_ylim(0,6000)
        ax.spines["top"].set_visible(False);ax.spines["right"].set_visible(False);ax.margins(x=0);ax.tick_params(axis="x",labelbottom=False)
    ax=axes[1,1];ax.axis("off")
    handles=[Line2D([0],[0],color="black",lw=1.4,label="Carico A65"),Line2D([0],[0],color=NET_COLOR,lw=1.7,ls="--",label=NET_LABEL + " + import netto A11"),Patch(facecolor="#2e8b57",alpha=.3,label="Surplus adj"),Patch(facecolor="#c00000",alpha=.3,label="Deficit adj"),Line2D([0],[0],color="#c00000",marker="|",lw=0,markersize=8,label="Prezzo zero MGP")]
    ax.legend(handles=handles,loc="upper center",fontsize=8,frameon=False,bbox_to_anchor=(.5,.95))
    ax.text(.98,.02,"Tutte le serie e i calcoli: 15 min\nA11 Grecia: nativo PT60, gradino orario",ha="right",va="bottom",fontsize=7,transform=ax.transAxes,bbox=dict(boxstyle="round,pad=.25",fc="white",ec="#ccc",lw=.6))
    style_time(axes[1,0],labels=True)
    fig.suptitle("Saldo fisico residuo dopo gli scambi - 3 zone (15 min UTC)",fontweight="bold")
    fig.tight_layout(rect=[0,0,1,.97]);path=OUT/"surplus_adj_3zone_15min.png";fig.savefig(path,dpi=150,bbox_inches="tight");plt.close(fig);print("scritto:",path)


def plot_surplus_adj_macro(flows, zero_map, load, netgen):
    l=load[ZONES].sum(axis=1,min_count=len(ZONES));p=netgen[ZONES].sum(axis=1,min_count=len(ZONES))
    ext=flows[((flows.in_zone.isin(MACRO))&(~flows.out_zone.isin(MACRO)))|((flows.out_zone.isin(MACRO))&(~flows.in_zone.isin(MACRO)))].copy()
    ext["signed"]=np.where(ext.in_zone.isin(MACRO),ext.flow_physical_mw,-ext.flow_physical_mw)
    ni=ext.groupby("ts").signed.sum(min_count=1).reindex(l.index).fillna(0)
    supply=p+ni; bal=supply-l
    fig,ax=plt.subplots(figsize=(14,6),dpi=150)
    ax.plot(l.index,l,color="black",lw=1.6,label="Carico A65")
    ax.plot(l.index,supply,color=NET_COLOR,lw=1.7,ls="--",label=NET_LABEL + " + import netto A11")
    ax.fill_between(l.index,supply,l,where=bal>0,color="#2e8b57",alpha=.35,label="Surplus adj",interpolate=True)
    ax.fill_between(l.index,supply,l,where=bal<0,color="#c00000",alpha=.35,label="Deficit adj",interpolate=True)
    ticks=sorted(set().union(*(set(zero_map[z]) for z in ZONES)));zero_ticks(ax,pd.DatetimeIndex(ticks))
    ax.axhline(0,color="#555",lw=.7,ls="--");ax.set_ylabel("MW");ax.grid(axis="y",color="#ddd",lw=.4)
    ax.legend(loc="lower right",fontsize=8);style_time(ax,labels=True)
    ax.set_title("Surplus adj macrozona Sud-Calabria-Sicilia (15 min UTC)",fontweight="bold")
    fig.tight_layout();path=OUT/"surplus_adj_macrozone_15min.png";fig.savefig(path,dpi=150,bbox_inches="tight");plt.close(fig);print("scritto:",path)


def main():
    flows, _, zero_map, load, gen, netgen, raw = load_inputs()
    plot_daily_bars(flows)
    plot_lines(flows, zero_map)
    plot_macrozone(flows, zero_map)
    plot_production_netimport(flows, zero_map, load, gen, netgen, raw)
    plot_surplus_adj(flows, zero_map, load, netgen)
    plot_surplus_adj_macro(flows, zero_map, load, netgen)
    print("Fatto. A11 Grecia è nativo PT60, visualizzato a gradino; NTC Sud-CentroSud resta nel grafico orario originale.")


if __name__ == "__main__":
    main()
